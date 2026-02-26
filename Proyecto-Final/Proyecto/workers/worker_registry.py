"""
Worker Registry: Registro centralizado de workers activos.

Mantiene un registro en Redis de todos los workers que están vivos,
usando heartbeats para detectar workers muertos.
"""
import time
import redis
from typing import Dict, List, Optional
from datetime import datetime


class WorkerRegistry:
    """
    Registro de workers activos en Redis.
    
    Cada worker debe:
    1. Registrarse al iniciar
    2. Enviar heartbeats periódicos
    3. Des-registrarse al terminar
    
    El registry puede:
    - Listar workers activos
    - Detectar workers muertos (sin heartbeat)
    - Limpiar workers muertos
    """
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        heartbeat_timeout: int = 30  # Segundos sin heartbeat = muerto
    ):
        """
        Inicializa el registro de workers.
        
        Args:
            redis_host: Host de Redis
            redis_port: Puerto de Redis
            heartbeat_timeout: Segundos sin heartbeat para considerar worker muerto
        """
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True
        )
        self.heartbeat_timeout = heartbeat_timeout
        self.registry_key = "worker_registry:workers"  # Hash de workers
    
    def register_worker(self, worker_id: str, metadata: Optional[Dict] = None) -> bool:
        """
        Registra un nuevo worker en el registry.
        
        Args:
            worker_id: ID único del worker
            metadata: Metadata opcional del worker (e.g., hostname, pid)
        
        Returns:
            True si se registró exitosamente
        """
        worker_info = {
            "worker_id": worker_id,
            "registered_at": datetime.utcnow().isoformat(),
            "last_heartbeat": time.time(),
            "status": "active"
        }
        
        # Agregar metadata adicional si se proporciona
        if metadata:
            worker_info.update(metadata)
        
        # Guardar en Redis como hash
        pipe = self.redis.pipeline()
        for key, value in worker_info.items():
            pipe.hset(f"{self.registry_key}:{worker_id}", key, str(value))
        pipe.execute()
        
        print(f"✅ Worker registrado: {worker_id}")
        return True
    
    def send_heartbeat(self, worker_id: str) -> bool:
        """
        Envía un heartbeat para indicar que el worker está vivo.
        
        Args:
            worker_id: ID del worker
        
        Returns:
            True si el heartbeat fue exitoso
        """
        # Actualizar timestamp del último heartbeat
        success = self.redis.hset(
            f"{self.registry_key}:{worker_id}",
            "last_heartbeat",
            str(time.time())
        )
        return success is not None
    
    def unregister_worker(self, worker_id: str) -> bool:
        """
        Des-registra un worker (cuando termina limpiamente).
        
        Args:
            worker_id: ID del worker
        
        Returns:
            True si se des-registró exitosamente
        """
        deleted = self.redis.delete(f"{self.registry_key}:{worker_id}")
        if deleted:
            print(f"👋 Worker des-registrado: {worker_id}")
        return deleted > 0
    
    def get_active_workers(self) -> List[Dict]:
        """
        Obtiene lista de workers activos (con heartbeat reciente).
        
        Returns:
            Lista de información de workers activos
        """
        active_workers = []
        current_time = time.time()
        
        # Buscar todas las keys de workers
        worker_keys = self.redis.keys(f"{self.registry_key}:*")
        
        for key in worker_keys:
            worker_info = self.redis.hgetall(key)
            
            if not worker_info:
                continue
            
            # Verificar si el heartbeat es reciente
            last_heartbeat = float(worker_info.get("last_heartbeat", 0))
            time_since_heartbeat = current_time - last_heartbeat
            
            if time_since_heartbeat < self.heartbeat_timeout:
                # Worker activo
                worker_info["time_since_heartbeat"] = round(time_since_heartbeat, 2)
                worker_info["is_alive"] = True
                active_workers.append(worker_info)
        
        return active_workers
    
    def get_dead_workers(self) -> List[Dict]:
        """
        Obtiene lista de workers muertos (sin heartbeat reciente).
        
        Returns:
            Lista de información de workers muertos
        """
        dead_workers = []
        current_time = time.time()
        
        worker_keys = self.redis.keys(f"{self.registry_key}:*")
        
        for key in worker_keys:
            worker_info = self.redis.hgetall(key)
            
            if not worker_info:
                continue
            
            last_heartbeat = float(worker_info.get("last_heartbeat", 0))
            time_since_heartbeat = current_time - last_heartbeat
            
            if time_since_heartbeat >= self.heartbeat_timeout:
                # Worker muerto
                worker_info["time_since_heartbeat"] = round(time_since_heartbeat, 2)
                worker_info["is_alive"] = False
                dead_workers.append(worker_info)
        
        return dead_workers
    
    def cleanup_dead_workers(self) -> int:
        """
        Elimina workers muertos del registro.
        
        Returns:
            Número de workers eliminados
        """
        dead_workers = self.get_dead_workers()
        count = 0
        
        for worker in dead_workers:
            worker_id = worker.get("worker_id")
            if worker_id:
                self.unregister_worker(worker_id)
                count += 1
        
        if count > 0:
            print(f"🧹 Limpiados {count} worker(s) muerto(s)")
        
        return count
    
    def get_worker_info(self, worker_id: str) -> Optional[Dict]:
        """
        Obtiene información de un worker específico.
        
        Args:
            worker_id: ID del worker
        
        Returns:
            Información del worker o None si no existe
        """
        worker_info = self.redis.hgetall(f"{self.registry_key}:{worker_id}")
        
        if not worker_info:
            return None
        
        # Agregar información de salud
        last_heartbeat = float(worker_info.get("last_heartbeat", 0))
        time_since_heartbeat = time.time() - last_heartbeat
        worker_info["time_since_heartbeat"] = round(time_since_heartbeat, 2)
        worker_info["is_alive"] = time_since_heartbeat < self.heartbeat_timeout
        
        return worker_info
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas del registry.
        
        Returns:
            Estadísticas generales
        """
        active_workers = self.get_active_workers()
        dead_workers = self.get_dead_workers()
        
        return {
            "total_registered": len(active_workers) + len(dead_workers),
            "active": len(active_workers),
            "dead": len(dead_workers),
            "heartbeat_timeout_seconds": self.heartbeat_timeout
        }
    
    def clear(self):
        """
        Limpia todo el registro (útil para testing).
        """
        worker_keys = self.redis.keys(f"{self.registry_key}:*")
        if worker_keys:
            self.redis.delete(*worker_keys)
        print("🧹 Registry limpiado")

