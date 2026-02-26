"""
Demo 2: Monitorear el sistema dockerizado.

Este script monitorea el estado de los workers y la cola.

Requisitos:
- Docker Compose debe estar corriendo
- pip install redis

Uso:
    python demo_monitor.py
"""
import redis
import json
import time
from datetime import datetime


def format_timestamp(ts: float) -> str:
    """Formatea un timestamp Unix."""
    return datetime.fromtimestamp(ts).strftime("%H:%M:%S")


def monitor_system(redis_client: redis.StrictRedis):
    """Monitorea el sistema en tiempo real."""
    print("=" * 70)
    print("📊 DEMO 2: Monitor del sistema")
    print("=" * 70)
    print("Presiona Ctrl+C para salir\n")
    
    try:
        while True:
            # Limpiar pantalla (compatible con Windows y Unix)
            print("\033[H\033[J", end="")
            
            print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 70)
            
            # Estado de la cola
            pending = redis_client.llen("image_processing_v2:pending")
            processing = redis_client.llen("image_processing_v2:processing")
            completed = redis_client.llen("image_processing_v2:completed")
            failed = redis_client.scard("image_processing_v2:failed")
            dlq = redis_client.llen("image_processing_v2:dlq")
            
            print("\n📦 COLA DE TAREAS:")
            print(f"   🔵 Pendientes:  {pending:3d}")
            print(f"   🟡 Procesando:  {processing:3d}")
            print(f"   🟢 Completadas: {completed:3d}")
            print(f"   🔴 Fallidas:    {failed:3d}")
            print(f"   ⚫ DLQ:         {dlq:3d}")
            
            # Workers activos
            print("\n👷 WORKERS ACTIVOS:")
            # Los workers están en keys separados: worker_registry:workers:worker-X
            worker_keys = redis_client.keys("worker_registry:workers:*")
            
            if worker_keys:
                for worker_key in worker_keys:
                    worker_data = redis_client.hgetall(worker_key)
                    if worker_data:
                        worker_id = worker_data.get("worker_id", worker_key.split(":")[-1])
                        last_heartbeat_ts = float(worker_data.get("last_heartbeat", 0))
                        last_heartbeat = format_timestamp(last_heartbeat_ts)
                        tasks = worker_data.get("tasks_processed", 0)
                        
                        # Calcular tiempo desde último heartbeat
                        elapsed = time.time() - last_heartbeat_ts
                        status = "🟢" if elapsed < 30 else "🔴"
                        
                        print(f"   {status} {worker_id}")
                        print(f"      💓 Último heartbeat: {last_heartbeat} ({elapsed:.0f}s)")
                        print(f"      ✅ Tareas completadas: {tasks}")
            else:
                print("   ⚠️  No hay workers activos")
            
            # Tareas recientes en procesamiento
            print("\n🔄 TAREAS EN PROCESAMIENTO:")
            processing_tasks = redis_client.lrange("image_processing_v2:processing", 0, 4)
            
            if processing_tasks:
                for task_str in processing_tasks[:3]:
                    task = json.loads(task_str)
                    task_id = task.get("task_id", "unknown")[:12]
                    output = task.get("output_path", "unknown").split("/")[-1]
                    print(f"   ⚙️  {task_id}... → {output}")
                
                if len(processing_tasks) > 3:
                    print(f"   ... y {len(processing_tasks) - 3} más")
            else:
                print("   (ninguna)")
            
            print("\n" + "=" * 70)
            print("💡 docker-compose logs -f para ver logs detallados")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n👋 Monitor detenido")


def main():
    """Demo principal."""
    # Conectar a Redis
    redis_client = redis.StrictRedis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True
    )
    
    # Verificar conexión
    try:
        redis_client.ping()
    except redis.ConnectionError:
        print("❌ No se pudo conectar a Redis")
        print("💡 Asegúrate de ejecutar: docker-compose up -d")
        return
    
    monitor_system(redis_client)


if __name__ == "__main__":
    main()

