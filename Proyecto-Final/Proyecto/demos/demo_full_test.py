"""
Demo 3: Test completo del sistema dockerizado.

Este script ejecuta un test end-to-end del sistema.

Requisitos:
- Docker Compose debe estar corriendo
- pip install redis Pillow

Uso:
    python demo_full_test.py
"""
import redis
import json
import uuid
import time
from pathlib import Path


def clear_redis(redis_client: redis.StrictRedis):
    """Limpia todas las colas de Redis."""
    keys_to_delete = [
        "image_processing_v2:pending",
        "image_processing_v2:processing",
        "image_processing_v2:completed",
        "image_processing_v2:failed",
        "image_processing_v2:dlq"
    ]
    
    for key in keys_to_delete:
        redis_client.delete(key)
    
    # Limpiar tasks individuales
    for key in redis_client.scan_iter("image_processing_v2:task:*"):
        redis_client.delete(key)


def send_task(redis_client: redis.StrictRedis, task: dict) -> str:
    """Envía una tarea usando el formato de RedisTaskQueueV2."""
    task_id = str(uuid.uuid4())
    task["task_id"] = task_id
    
    # Guardar task data como hash
    task_key = f"image_processing_v2:task:{task_id}"
    pipe = redis_client.pipeline()
    
    for key, value in task.items():
        pipe.hset(task_key, key, json.dumps(value))
    
    # Agregar task_id a la cola
    pipe.lpush("image_processing_v2:pending", task_id)
    pipe.execute()
    
    return task_id


def wait_for_completion(
    redis_client: redis.StrictRedis,
    task_ids: list,
    timeout: int = 60
) -> dict:
    """
    Espera a que todas las tareas se completen.
    
    Returns:
        Diccionario con resultados
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        completed_count = 0
        failed_count = 0
        
        # Obtener todas las tareas completadas y fallidas
        completed_tasks = redis_client.lrange("image_processing_v2:completed", 0, -1)
        failed_tasks = redis_client.smembers("image_processing_v2:failed")
        
        for task_id in task_ids:
            if task_id in completed_tasks:
                completed_count += 1
            elif task_id in failed_tasks:
                failed_count += 1
        
        if completed_count + failed_count == len(task_ids):
            return {
                "completed": completed_count,
                "failed": failed_count,
                "time": time.time() - start_time
            }
        
        time.sleep(0.5)
    
    return {
        "completed": completed_count,
        "failed": failed_count,
        "time": time.time() - start_time,
        "timeout": True
    }


def main():
    """Test completo."""
    print("=" * 70)
    print("🧪 DEMO 3: Test completo del sistema")
    print("=" * 70)
    
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
        print("✅ Conectado a Redis")
    except redis.ConnectionError:
        print("❌ No se pudo conectar a Redis")
        return
    
    # Verificar workers
    worker_keys = redis_client.keys("worker_registry:workers:*")
    print(f"✅ Workers activos: {len(worker_keys)}")
    
    if len(worker_keys) == 0:
        print("⚠️  No hay workers activos. Ejecuta: docker-compose up -d")
        return
    
    # Limpiar Redis
    print("\n🧹 Limpiando Redis...")
    clear_redis(redis_client)
    time.sleep(1)
    
    # Crear tareas
    print("\n📤 Enviando 10 tareas...")
    tasks = []
    task_ids = []
    
    filters_combinations = [
        [{"type": "blur", "radius": 3}],
        [{"type": "brightness", "factor": 1.5}],
        [{"type": "edges"}],
        [{"type": "grayscale"}],
        [{"type": "blur", "radius": 5}],
        [{"type": "grayscale"}, {"type": "edges"}],
        [{"type": "brightness", "factor": 0.7}],
        [{"type": "grayscale"}, {"type": "blur", "radius": 2}],
        [{"type": "edges"}, {"type": "brightness", "factor": 1.2}],
        [{"type": "blur", "radius": 2}, {"type": "brightness", "factor": 1.3}]
    ]
    
    for i, filters in enumerate(filters_combinations):
        task = {
            "input_path": "images/sample.jpg",
            "output_path": f"output/test_{i}.jpg",
            "filters": filters
        }
        task_id = send_task(redis_client, task)
        tasks.append(task)
        task_ids.append(task_id)
        
        filters_str = " → ".join(f["type"] for f in filters)
        print(f"  {i+1}. test_{i}.jpg: {filters_str}")
    
    # Esperar procesamiento
    print(f"\n⏳ Esperando procesamiento...")
    result = wait_for_completion(redis_client, task_ids, timeout=60)
    
    # Resultados
    print("\n" + "=" * 70)
    print("📊 RESULTADOS:")
    print("=" * 70)
    
    print(f"✅ Completadas: {result['completed']}/{len(task_ids)}")
    print(f"❌ Fallidas:    {result['failed']}/{len(task_ids)}")
    print(f"⏱️  Tiempo:      {result['time']:.2f}s")
    
    if result.get("timeout"):
        print("⚠️  Timeout alcanzado")
    
    # Verificar archivos de salida
    print("\n📁 Verificando archivos de salida:")
    output_dir = Path("output")
    
    for i in range(len(tasks)):
        output_file = output_dir / f"test_{i}.jpg"
        if output_file.exists():
            size_kb = output_file.stat().st_size / 1024
            print(f"  ✅ test_{i}.jpg ({size_kb:.1f} KB)")
        else:
            print(f"  ❌ test_{i}.jpg (no encontrado)")
    
    # Estadísticas de workers
    print("\n👷 Estadísticas de workers:")
    worker_keys = redis_client.keys("worker_registry:workers:*")
    
    for worker_key in sorted(worker_keys):
        worker_data = redis_client.hgetall(worker_key)
        if worker_data:
            worker_id = worker_data.get("worker_id", worker_key.split(":")[-1])
            tasks_processed = worker_data.get("tasks_processed", 0)
            print(f"  {worker_id}: {tasks_processed} tareas")
    
    print("\n" + "=" * 70)
    print("✅ Test completado")
    print("=" * 70)


if __name__ == "__main__":
    main()

