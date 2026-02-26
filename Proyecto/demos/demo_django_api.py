import requests
import time
import json
from pathlib import Path


DJANGO_API_URL = "http://localhost:8000/api"


def send_task(filters: list, image_path: str, output_name: str) -> dict:
    """
    Envía una tarea a Django API via POST HTTP.
    Django se encarga de encolarla en Redis.
    """
    response = requests.post(
        f"{DJANGO_API_URL}/process/",
        json={
            "filters": filters,
            "image_path": image_path,
            "output_name": output_name
        }
    )
    return response.json()


def check_task_status(task_id: str) -> dict:
    """Consulta el estado de una tarea via Django API."""
    response = requests.get(f"{DJANGO_API_URL}/task/{task_id}/")
    return response.json()


def get_workers_status() -> dict:
    """Consulta workers activos via Django API."""
    response = requests.get(f"{DJANGO_API_URL}/workers/")
    return response.json()


def wait_for_tasks(task_ids: list, timeout: int = 30) -> dict:
    """
    Espera a que todas las tareas terminen.
    Consulta el estado cada segundo.
    """
    start_time = time.time()
    results = {}

    print("\n⏳ Esperando resultados...\n")

    while len(results) < len(task_ids):
        if time.time() - start_time > timeout:
            print("⚠️  Timeout esperando tareas")
            break

        for task_id in task_ids:
            if task_id in results:
                continue

            status = check_task_status(task_id)
            task_status = status.get('status', 'unknown')

            if task_status in ('completed', 'dead'):
                results[task_id] = status
                icon = "✅" if task_status == "completed" else "❌"
                print(f"  {icon} {task_id[:20]}... → {task_status}")

        time.sleep(1)

    return results


def main():
    print("=" * 70)
    print("🚀 DEMO: Enviar tareas via Django API")
    print("=" * 70)

    # 1. Verificar que Django responde
    try:
        response = requests.get(f"{DJANGO_API_URL}/health/")
        health = response.json()
        print(f"✅ Django API: {health['status']}")
        print(f"✅ Redis: {health['redis']}\n")
    except Exception as e:
        print(f"❌ No se pudo conectar a Django API: {e}")
        print("💡 Asegúrate de ejecutar: docker-compose up -d")
        return

    # 2. Verificar workers activos
    workers = get_workers_status()
    print(f"👷 Workers activos: {workers['active_workers']}")
    for w in workers['workers']:
        print(f"   - {w['id']} ({w['status']})")

    # 3. Verificar imagen de entrada
    if not Path("images/sample.jpg").exists():
        print("\n❌ No se encontró images/sample.jpg")
        return

    # 4. Definir 5 tareas con filtros diferentes
    tareas = [
        {
            "filters": ["blur"],
            "image_path": "images/sample.jpg",
            "output_name": "blur.jpg",
            "descripcion": "Desenfoque gaussiano"
        },
        {
            "filters": ["grayscale"],
            "image_path": "images/sample.jpg",
            "output_name": "grayscale.jpg",
            "descripcion": "Blanco y negro"
        },
        {
            "filters": ["edges"],
            "image_path": "images/sample.jpg",
            "output_name": "edges.jpg",
            "descripcion": "Detección de bordes"
        },
        {
            "filters": ["brightness"],
            "image_path": "images/sample.jpg",
            "output_name": "brightness.jpg",
            "descripcion": "Aumento de brillo"
        },
        {
            "filters": ["grayscale", "edges"],
            "image_path": "images/sample.jpg",
            "output_name": "combo.jpg",
            "descripcion": "Combinado: grayscale + edges"
        }
    ]

    # 5. Enviar todas las tareas
    print(f"\n📤 Enviando {len(tareas)} tareas a Django API...\n")
    start_time = time.time()

    task_ids = []
    for i, tarea in enumerate(tareas, 1):
        result = send_task(
            filters=tarea["filters"],
            image_path=tarea["image_path"],
            output_name=tarea["output_name"]
        )
        task_id = result.get("task_id")
        task_ids.append(task_id)
        filters_str = " → ".join(tarea["filters"])
        print(f"  {i}. [{filters_str}] {tarea['descripcion']}")
        print(f"     Task ID: {task_id}")

    print(f"\n✅ {len(task_ids)} tareas encoladas via Django API")

    # 6. Esperar resultados
    results = wait_for_tasks(task_ids)

    # 7. Mostrar resumen
    total_time = time.time() - start_time
    completed = sum(1 for r in results.values() if r.get('status') == 'completed')
    failed = sum(1 for r in results.values() if r.get('status') == 'dead')

    print("\n" + "=" * 70)
    print("📊 RESULTADOS:")
    print("=" * 70)
    print(f"✅ Completadas: {completed}/{len(tareas)}")
    print(f"❌ Fallidas:    {failed}/{len(tareas)}")
    print(f"⏱️  Tiempo:      {total_time:.2f}s")

    print("\n📁 Archivos generados en output/:")
    for tarea in tareas:
        output_file = Path(__file__).parent.parent / "output" / tarea["output_name"]
        if output_file.exists():
            size_kb = output_file.stat().st_size / 1024
            print(f"  ✅ {tarea['output_name']} ({size_kb:.1f} KB)")
        else:
            print(f"  ❌ {tarea['output_name']} no encontrado")

    print("\n👷 Estado final de workers:")
    workers_final = get_workers_status()
    for w in workers_final['workers']:
        print(f"  {w['id']}: activo")


if __name__ == "__main__":
    main()