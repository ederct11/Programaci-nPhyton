"""
MonitoredRedisWorker: Worker con health checks y heartbeats.

Mejoras respecto a RedisWorker (Sesión 4):
- Se registra en WorkerRegistry al iniciar
- Envía heartbeats periódicos
- Se des-registra al terminar (graceful shutdown)
- Maneja interrupciones (Ctrl+C) correctamente
"""
import time
import signal
import logging
from typing import Optional
from pathlib import Path
from PIL import Image

from .worker_registry import WorkerRegistry
from .redis_task_queue_v2 import RedisTaskQueueV2

# Copiar filtros de sesión anterior
import sys
sys.path.append(str(Path(__file__).parent.parent))
from filters import BlurFilter, BrightnessFilter, EdgesFilter, GrayscaleFilter
from core import FilterPipeline, FilterFactory


class MonitoredRedisWorker:
    """
    Worker que procesa tareas de Redis con monitoring.
    
    Características:
    - Se registra en WorkerRegistry
    - Envía heartbeats cada N segundos
    - Maneja graceful shutdown (SIGINT, SIGTERM)
    - Procesa tareas de RedisTaskQueueV2
    """
    
    def __init__(
        self,
        worker_id: str,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        heartbeat_interval: int = 10  # Segundos entre heartbeats
    ):
        """
        Inicializa el worker monitoreado.
        
        Args:
            worker_id: ID único del worker
            redis_host: Host de Redis
            redis_port: Puerto de Redis
            heartbeat_interval: Segundos entre heartbeats
        """
        self.worker_id = worker_id
        self.heartbeat_interval = heartbeat_interval
        self.running = False
        
        # Conectar a Redis
        self.queue = RedisTaskQueueV2(
            redis_host=redis_host,
            redis_port=redis_port
        )
        
        self.registry = WorkerRegistry(
            redis_host=redis_host,
            redis_port=redis_port
        )
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format=f'[{worker_id}] %(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(worker_id)
        
        # Estadísticas
        self.tasks_processed = 0
        self.tasks_failed = 0
        self.last_heartbeat = 0
        
        # Configurar signal handlers para graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.logger.info(f"✨ Worker inicializado: {worker_id}")
    
    def _signal_handler(self, signum, frame):
        """Maneja señales de interrupción (Ctrl+C, kill)."""
        self.logger.info("⚠️  Señal de interrupción recibida, cerrando...")
        self.stop()
    
    def start(self):
        """
        Inicia el worker.
        
        1. Registra el worker en el registry
        2. Envía heartbeats periódicos
        3. Procesa tareas de la cola
        """
        self.running = True
        
        # Registrar en el registry
        self.registry.register_worker(
            self.worker_id,
            metadata={
                "heartbeat_interval": self.heartbeat_interval,
                "started_at": time.time()
            }
        )
        
        self.logger.info("🚀 Worker iniciado, esperando tareas...")
        
        try:
            while self.running:
                # Enviar heartbeat si es necesario
                self._send_heartbeat_if_needed()
                
                # Obtener tarea de la cola (timeout=5s para no bloquear heartbeats)
                task = self.queue.get_task(self.worker_id, timeout=5)
                
                if task:
                    self._process_task(task)
                else:
                    # No hay tareas, seguir esperando
                    continue
        
        except Exception as e:
            self.logger.error(f"❌ Error fatal: {e}")
        
        finally:
            self._shutdown()
    
    def stop(self):
        """
        Detiene el worker (graceful shutdown).
        """
        self.running = False
    
    def _send_heartbeat_if_needed(self):
        """
        Envía heartbeat si ha pasado el intervalo.
        """
        current_time = time.time()
        
        if current_time - self.last_heartbeat >= self.heartbeat_interval:
            self.registry.send_heartbeat(self.worker_id)
            self.last_heartbeat = current_time
            self.logger.debug(f"💓 Heartbeat enviado")
    
    def _process_task(self, task: dict):
        """
        Procesa una tarea.
        
        Args:
            task: Tarea a procesar
        """
        task_id = task.get("task_id")
        retry_count = int(task.get("retry_count", 0))
        
        self.logger.info(f"📝 Procesando {task_id} (retry={retry_count})")
        
        start_time = time.time()
        
        try:
            # Extraer parámetros directamente de task (sin "data" wrapper)
            input_path = task.get("input_path")
            output_path = task.get("output_path")
            filters_config = task.get("filters", [])
            
            if not input_path or not output_path:
                raise ValueError("Missing input_path or output_path")
            
            # Cargar imagen
            image = Image.open(input_path)
            
            # Crear pipeline de filtros
            factory = FilterFactory()
            pipeline = factory.create_pipeline(filters_config)
            
            # Aplicar filtros (devuelve tupla: image, timing_info)
            processed_image, timing_info = pipeline.apply(image)
            
            # Crear directorio de salida si no existe
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Guardar resultado
            processed_image.save(output_path, quality=95)
            
            # Marcar como completada
            elapsed = time.time() - start_time
            self.queue.mark_completed(task_id, {
                "output_path": output_path,
                "elapsed_seconds": round(elapsed, 2)
            })
            
            self.tasks_processed += 1
            self.logger.info(f"✅ {task_id} completada en {elapsed:.2f}s")
        
        except Exception as e:
            # Marcar como fallida (se reintentará automáticamente)
            elapsed = time.time() - start_time
            self.queue.mark_failed(task_id, str(e))
            
            self.tasks_failed += 1
            self.logger.error(f"❌ {task_id} falló: {e}")
    
    def _shutdown(self):
        """
        Cierre limpio del worker.
        """
        self.logger.info("🛑 Cerrando worker...")
        
        # Des-registrar del registry
        self.registry.unregister_worker(self.worker_id)
        
        # Mostrar estadísticas finales
        self.logger.info(
            f"📊 Estadísticas: {self.tasks_processed} completadas, "
            f"{self.tasks_failed} fallidas"
        )
        
        self.logger.info("👋 Worker cerrado correctamente")
    
    def get_stats(self) -> dict:
        """
        Obtiene estadísticas del worker.
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            "worker_id": self.worker_id,
            "tasks_processed": self.tasks_processed,
            "tasks_failed": self.tasks_failed,
            "is_running": self.running
        }


if __name__ == "__main__":
    import os
    import uuid
    
    # Configuración desde variables de entorno
    worker_id = os.getenv("WORKER_ID", f"worker-{uuid.uuid4().hex[:8]}")
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    heartbeat_interval = int(os.getenv("HEARTBEAT_INTERVAL", "10"))
    
    print(f"🚀 Iniciando {worker_id}")
    print(f"📡 Redis: {redis_host}:{redis_port}")
    print(f"💓 Heartbeat interval: {heartbeat_interval}s")
    
    # Crear y ejecutar worker
    worker = MonitoredRedisWorker(
        worker_id=worker_id,
        redis_host=redis_host,
        redis_port=redis_port,
        heartbeat_interval=heartbeat_interval
    )
    
    worker.start()

