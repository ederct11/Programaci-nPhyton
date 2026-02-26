"""
RedisTaskQueueV2: Cola de tareas con auto-recovery y dead letter queue.

Mejoras respecto a RedisTaskQueue (Sesión 4):
- Reintentos automáticos de tareas fallidas
- Dead Letter Queue para tareas irrecuperables
- Contadores de reintentos
- Timeout para tareas atascadas
"""
import json
import time
import redis
from typing import Dict, Optional, Any
from datetime import datetime


class RedisTaskQueueV2:
    """
    Cola de tareas distribuida en Redis con auto-recovery.
    
    Estados de tareas:
    - pending: En cola, esperando ser procesada
    - processing: Siendo procesada por un worker
    - completed: Completada exitosamente
    - failed: Falló y será reintentada
    - dead: Falló demasiadas veces (Dead Letter Queue)
    
    Flujo de reintentos:
    1. Tarea falla → mark_failed()
    2. Se incrementa retry_count
    3. Si retry_count < max_retries → va a pending
    4. Si retry_count >= max_retries → va a dead letter queue
    """
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        queue_name: str = "image_processing_v2",
        max_retries: int = 3,
        processing_timeout: int = 300  # 5 minutos
    ):
        """
        Inicializa la cola de tareas V2.
        
        Args:
            redis_host: Host de Redis
            redis_port: Puerto de Redis
            queue_name: Nombre de la cola
            max_retries: Número máximo de reintentos antes de DLQ
            processing_timeout: Segundos antes de considerar tarea atascada
        """
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
        self.queue_name = queue_name
        self.max_retries = max_retries
        self.processing_timeout = processing_timeout
        
        # Keys de Redis
        self.pending_key = f"{queue_name}:pending"
        self.processing_key = f"{queue_name}:processing"
        self.completed_key = f"{queue_name}:completed"
        self.failed_key = f"{queue_name}:failed"
        self.dead_letter_key = f"{queue_name}:dead_letter"  # 🆕 DLQ
        
        print(f"✅ RedisTaskQueueV2 inicializada: {queue_name} (max_retries={max_retries})")
    
    def add_task(self, task_data: Dict[str, Any]) -> str:
        """
        Agrega una tarea a la cola.
        
        Args:
            task_data: Datos de la tarea (debe incluir 'input_path', 'output_path', etc.)
        
        Returns:
            ID de la tarea
        """
        task_id = f"task-{int(time.time() * 1000)}"
        
        # Crear metadata de la tarea
        task = {
            "task_id": task_id,
            "data": task_data,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "retry_count": 0,  # 🆕 Contador de reintentos
            "last_error": None
        }
        
        # Guardar tarea en Redis (hash)
        self.redis.hset(f"{self.queue_name}:task:{task_id}", mapping={
            k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            for k, v in task.items()
        })
        
        # Agregar a cola pending (lista)
        self.redis.rpush(self.pending_key, task_id)
        
        print(f"📥 Tarea agregada: {task_id}")
        return task_id
    
    def get_task(self, worker_id: str, timeout: int = 5) -> Optional[Dict]:
        """
        Obtiene una tarea de la cola (operación bloqueante y atómica).
        
        Usa BRPOPLPUSH para mover atómicamente de pending → processing.
        
        Args:
            worker_id: ID del worker que procesa la tarea
            timeout: Segundos a esperar si no hay tareas
        
        Returns:
            Tarea o None si no hay tareas disponibles
        """
        # BRPOPLPUSH: Mueve atómicamente de pending a processing
        task_id = self.redis.brpoplpush(
            self.pending_key,
            self.processing_key,
            timeout=timeout
        )
        
        if not task_id:
            return None
        
        # Obtener datos de la tarea
        task_key = f"{self.queue_name}:task:{task_id}"
        task_data = self.redis.hgetall(task_key)
        
        if not task_data:
            # Tarea no existe (error raro)
            self.redis.lrem(self.processing_key, 1, task_id)
            return None
        
        # Parsear JSON fields
        task = {}
        for key, value in task_data.items():
            try:
                task[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                task[key] = value
        
        # Actualizar metadata
        pipe = self.redis.pipeline()
        pipe.hset(task_key, "status", "processing")
        pipe.hset(task_key, "worker_id", worker_id)
        pipe.hset(task_key, "started_at", datetime.utcnow().isoformat())
        pipe.execute()
        
        return task
    
    def mark_completed(self, task_id: str, result: Optional[Dict] = None):
        """
        Marca una tarea como completada exitosamente.
        
        Args:
            task_id: ID de la tarea
            result: Resultado opcional de la tarea
        """
        # Remover de processing
        self.redis.lrem(self.processing_key, 1, task_id)
        
        # Actualizar metadata
        pipe = self.redis.pipeline()
        pipe.hset(f"{self.queue_name}:task:{task_id}", "status", "completed")
        pipe.hset(f"{self.queue_name}:task:{task_id}", "completed_at", datetime.utcnow().isoformat())
        if result:
            pipe.hset(f"{self.queue_name}:task:{task_id}", "result", json.dumps(result))
        
        # Agregar a lista de completadas
        pipe.rpush(self.completed_key, task_id)
        pipe.execute()
        
        print(f"✅ Tarea completada: {task_id}")
    
    def mark_failed(
        self,
        task_id: str,
        error_message: str,
        should_retry: bool = True
    ):
        """
        Marca una tarea como fallida.
        
        - Si retry_count < max_retries: reintenta (va a pending)
        - Si retry_count >= max_retries: va a Dead Letter Queue
        
        Args:
            task_id: ID de la tarea
            error_message: Mensaje de error
            should_retry: Si False, envía directo a DLQ
        """
        # Remover de processing
        self.redis.lrem(self.processing_key, 1, task_id)
        
        # Obtener retry_count actual
        task_data = self.redis.hgetall(f"{self.queue_name}:task:{task_id}")
        retry_count = int(task_data.get("retry_count", 0))
        retry_count += 1
        
        # Actualizar metadata
        pipe = self.redis.pipeline()
        pipe.hset(f"{self.queue_name}:task:{task_id}", "retry_count", retry_count)
        pipe.hset(f"{self.queue_name}:task:{task_id}", "last_error", error_message)
        pipe.hset(f"{self.queue_name}:task:{task_id}", "failed_at", datetime.utcnow().isoformat())
        
        # Decidir si reintentar o enviar a DLQ
        if should_retry and retry_count < self.max_retries:
            # Reintentar: volver a pending
            pipe.hset(f"{self.queue_name}:task:{task_id}", "status", "failed")
            pipe.rpush(self.pending_key, task_id)
            pipe.execute()
            print(f"⚠️  Tarea fallida (reintento {retry_count}/{self.max_retries}): {task_id}")
        else:
            # Dead Letter Queue: demasiados reintentos
            pipe.hset(f"{self.queue_name}:task:{task_id}", "status", "dead")
            pipe.rpush(self.dead_letter_key, task_id)
            pipe.execute()
            print(f"💀 Tarea en DLQ (reintentos agotados): {task_id}")
    
    def recover_stuck_tasks(self) -> int:
        """
        Recupera tareas atascadas en processing (sin avance por timeout).
        
        Una tarea se considera atascada si lleva más de processing_timeout
        segundos en el estado "processing".
        
        Returns:
            Número de tareas recuperadas
        """
        current_time = time.time()
        recovered = 0
        
        # Obtener todas las tareas en processing
        task_ids = self.redis.lrange(self.processing_key, 0, -1)
        
        for task_id in task_ids:
            task_key = f"{self.queue_name}:task:{task_id}"
            task_data = self.redis.hgetall(task_key)
            
            if not task_data:
                continue
            
            # Verificar cuánto tiempo lleva en processing
            started_at_str = task_data.get("started_at")
            if not started_at_str:
                continue
            
            try:
                started_at = datetime.fromisoformat(started_at_str)
                elapsed = (datetime.utcnow() - started_at).total_seconds()
                
                if elapsed > self.processing_timeout:
                    # Tarea atascada: recuperar
                    self.mark_failed(
                        task_id,
                        f"Timeout: sin progreso por {elapsed:.0f}s"
                    )
                    recovered += 1
            except (ValueError, TypeError):
                continue
        
        if recovered > 0:
            print(f"🔄 Recuperadas {recovered} tarea(s) atascada(s)")
        
        return recovered
    
    def get_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas de la cola.
        
        Returns:
            Diccionario con contadores
        """
        return {
            "pending": self.redis.llen(self.pending_key),
            "processing": self.redis.llen(self.processing_key),
            "completed": self.redis.llen(self.completed_key),
            "failed": self.redis.llen(self.failed_key),
            "dead_letter": self.redis.llen(self.dead_letter_key),  # 🆕
            "max_retries": self.max_retries
        }
    
    def get_dead_letter_tasks(self) -> list:
        """
        Obtiene todas las tareas en Dead Letter Queue.
        
        Returns:
            Lista de task_ids en DLQ
        """
        return self.redis.lrange(self.dead_letter_key, 0, -1)
    
    def retry_dead_letter_task(self, task_id: str):
        """
        Reintenta manualmente una tarea de la Dead Letter Queue.
        
        Útil para tareas que fallaron por errores temporales.
        
        Args:
            task_id: ID de la tarea a reintentar
        """
        # Remover de DLQ
        removed = self.redis.lrem(self.dead_letter_key, 1, task_id)
        
        if removed:
            # Reset retry_count y mover a pending
            pipe = self.redis.pipeline()
            pipe.hset(f"{self.queue_name}:task:{task_id}", "retry_count", 0)
            pipe.hset(f"{self.queue_name}:task:{task_id}", "status", "pending")
            pipe.rpush(self.pending_key, task_id)
            pipe.execute()
            print(f"🔄 Tarea reintentada desde DLQ: {task_id}")
    
    def clear(self):
        """
        Limpia toda la cola (útil para testing).
        """
        # Limpiar listas
        self.redis.delete(
            self.pending_key,
            self.processing_key,
            self.completed_key,
            self.failed_key,
            self.dead_letter_key
        )
        
        # Limpiar tasks y results
        task_keys = self.redis.keys("task:*")
        result_keys = self.redis.keys("result:*")
        if task_keys:
            self.redis.delete(*task_keys)
        if result_keys:
            self.redis.delete(*result_keys)
        
        print("🧹 Cola limpiada")

