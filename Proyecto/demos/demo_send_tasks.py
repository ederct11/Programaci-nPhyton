"""
Demo 1: Enviar tareas al sistema dockerizado.

Este script se ejecuta FUERA de Docker y envía tareas al sistema.

Requisitos:
- Docker Compose debe estar corriendo
- pip install redis Pillow

Uso:
    python demo_send_tasks.py
"""
import redis
import json
import uuid
from pathlib import Path


def send_task(redis_client: redis.StrictRedis, task: dict) -> str:
    """
    Envía una tarea a la cola de Redis usando el formato de RedisTaskQueueV2.
    
    Args:
        redis_client: Cliente de Redis
        task: Diccionario con la tarea
        
    Returns:
        ID de la tarea
    """
    task_id = task.get("task_id", str(uuid.uuid4()))
    task["task_id"] = task_id
    
    # Guardar task data como hash (RedisTaskQueueV2 lo espera así)
    task_key = f"image_processing_v2:task:{task_id}"
    pipe = redis_client.pipeline()
    
    for key, value in task.items():
        # Serializar todo como JSON
        pipe.hset(task_key, key, json.dumps(value))
    
    # Agregar el task_id a la cola pending
    pipe.lpush("image_processing_v2:pending", task_id)
    pipe.execute()
    
    return task_id


def main():
    """Demo principal."""
    print("=" * 70)
    print("🚀 DEMO 1: Enviar tareas al sistema dockerizado")
    print("=" * 70)
    
    # Conectar a Redis (expuesto en puerto 6379)
    redis_client = redis.StrictRedis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True
    )
    
    # Verificar conexión
    try:
        redis_client.ping()
        print("✅ Conectado a Redis\n")
    except redis.ConnectionError:
        print("❌ No se pudo conectar a Redis")
        print("💡 Asegúrate de ejecutar: docker-compose up -d")
        return
    
    # Verificar imagen de entrada
    input_image = Path("images/sample.jpg")
    if not input_image.exists():
        print(f"❌ No se encontró {input_image}")
        return
    
    # Tareas a enviar
    tasks = [
        {
            "input_path": "images/sample.jpg",
            "output_path": "output/blur.jpg",
            "filters": [{"type": "blur", "radius": 5}]
        },
        {
            "input_path": "images/sample.jpg",
            "output_path": "output/brightness.jpg",
            "filters": [{"type": "brightness", "factor": 1.5}]
        },
        {
            "input_path": "images/sample.jpg",
            "output_path": "output/edges.jpg",
            "filters": [{"type": "edges"}]
        },
        {
            "input_path": "images/sample.jpg",
            "output_path": "output/grayscale.jpg",
            "filters": [{"type": "grayscale"}]
        },
        {
            "input_path": "images/sample.jpg",
            "output_path": "output/combo.jpg",
            "filters": [
                {"type": "grayscale"},
                {"type": "edges"},
                {"type": "brightness", "factor": 1.3}
            ]
        }
    ]
    
    print(f"📤 Enviando {len(tasks)} tareas...\n")
    
    task_ids = []
    for i, task in enumerate(tasks, 1):
        task_id = send_task(redis_client, task)
        task_ids.append(task_id)
        
        filters_str = " → ".join(f["type"] for f in task["filters"])
        print(f"  {i}. {task['output_path']}: {filters_str}")
        print(f"     Task ID: {task_id}")
    
    print(f"\n✅ Enviadas {len(task_ids)} tareas")
    
    # Mostrar estadísticas de la cola
    pending = redis_client.llen("image_processing_v2:pending")
    processing = redis_client.llen("image_processing_v2:processing")
    completed = redis_client.llen("image_processing_v2:completed")
    
    print(f"\n📊 Estado de la cola:")
    print(f"   Pendientes: {pending}")
    print(f"   Procesando: {processing}")
    print(f"   Completadas: {completed}")
    
    print(f"\n💡 Monitorea los logs con: docker-compose logs -f")
    print(f"💡 Ver workers: docker-compose ps")
    print(f"💡 Ver resultados en: output/")


if __name__ == "__main__":
    main()

