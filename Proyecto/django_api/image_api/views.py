import json
import os
import time
import uuid
import redis
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Conexión a Redis usando variables de entorno de Docker
def get_redis():
    return redis.StrictRedis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=0,
        decode_responses=True
    )

# -------------------------------------------------------
# POST /api/process/
# Envía una tarea a la cola de Redis para que un worker la procese
# -------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def process_image(request):
    try:
        data = json.loads(request.body)
        filters = data.get('filters', ['blur'])
        image_path = data.get('image_path', 'images/sample.jpg')
        output_name = data.get('output_name', None)  

        task_id = f"task-{int(time.time() * 1000)}"
        queue_name = "image_processing_v2"

        filters_config = [{"type": f} for f in filters]

        
        final_output = output_name if output_name else f"{task_id}.jpg"

        task = {
            "task_id": task_id,
            "input_path": f"/app/{image_path}",
            "output_path": f"/app/output/{final_output}",
            "filters": json.dumps(filters_config),
            "status": "pending",
            "created_at": str(time.time()),
            "retry_count": "0",
            "last_error": "None"
        }

        r = get_redis()
        r.hset(f"{queue_name}:task:{task_id}", mapping=task)
        r.rpush(f"{queue_name}:pending", task_id)

        return JsonResponse({
            'success': True,
            'task_id': task_id,
            'output_name': final_output,
            'message': 'Tarea encolada, un worker la procesará',
            'check_status': f'/api/task/{task_id}/'
        })

    except Exception as e:
        import traceback
        return JsonResponse({'error': str(e), 'traceback': traceback.format_exc()}, status=500)


# -------------------------------------------------------
# GET /api/task/<task_id>/
# Consulta el estado de una tarea (la actualiza el worker)
# -------------------------------------------------------
@require_http_methods(["GET"])
def task_status(request, task_id):
    try:
        r = get_redis()
        task = r.hgetall(f"image_processing_v2:task:{task_id}")

        if not task:
            return JsonResponse({'error': 'Tarea no encontrada'}, status=404)

        return JsonResponse({
            'task_id': task_id,
            'status': task.get('status', 'unknown'),
            'output_path': task.get('output_path', None),
            'duration': task.get('duration', None),
            'worker_id': task.get('worker_id', None)
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# -------------------------------------------------------
# GET /api/workers/
# Muestra qué workers están activos y cuántas tareas procesaron
# -------------------------------------------------------
@require_http_methods(["GET"])
def workers_status(request):
    try:
        r = get_redis()

        worker_keys = r.keys('worker_registry:workers:*')
        workers = []

        for key in worker_keys:
            worker = r.hgetall(key)
            workers.append({
                'id': worker.get('worker_id'),
                'status': worker.get('status', 'unknown'),
                'last_heartbeat': worker.get('last_heartbeat', None),
                'registered_at': worker.get('registered_at', None),
            })

        queue_length = r.llen('task_queue')

        return JsonResponse({
            'active_workers': len(workers),
            'workers': workers,
            'queue': {
                'pending': queue_length
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# -------------------------------------------------------
# GET /api/health/
# Health check para Docker
# -------------------------------------------------------
def health_check(request):
    try:
        r = get_redis()
        r.ping()  # Verifica que Redis responde
        return JsonResponse({'status': 'healthy', 'redis': 'connected'})
    except Exception:
        return JsonResponse({'status': 'unhealthy', 'redis': 'disconnected'}, status=503)


@require_http_methods(["GET"])
def debug_redis(request):
    try:
        r = get_redis()
        keys = r.keys('*')
        result = {}
        for key in keys:
            key_type = r.type(key)
            if key_type == 'hash':
                result[key] = r.hgetall(key)
            elif key_type == 'list':
                result[key] = r.lrange(key, 0, -1)
            else:
                result[key] = r.get(key)
        return JsonResponse({'keys': result})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)