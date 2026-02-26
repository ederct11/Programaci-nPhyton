"""
Punto de entrada para ejecutar el worker como módulo.

Uso:
    python -m workers.monitored_redis_worker
"""
import os
import uuid
from .monitored_redis_worker import MonitoredRedisWorker


def main():
    """Ejecuta el worker monitoreado."""
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


if __name__ == "__main__":
    main()



