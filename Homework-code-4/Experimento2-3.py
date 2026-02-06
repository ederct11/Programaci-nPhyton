import time
import sys
from concurrent.futures import ProcessPoolExecutor

sys.set_int_max_str_digits(0)

def suma_factoriales_rango(args):
    """Calcula la suma de factoriales en un rango específico de forma optimizada"""
    inicio, fin, task_name = args
    print(f"{task_name}: Procesando rango [{inicio}, {fin}]...")
    tiempo_inicio = time.time()
    
    suma_parcial = 0
    factorial_actual = 1
    
    for i in range(1, inicio):
        factorial_actual *= i
    
    for i in range(inicio, fin + 1):
        factorial_actual *= i
        suma_parcial += factorial_actual
    
    tiempo_fin = time.time()
    print(f"{task_name}: Completado en {tiempo_fin - tiempo_inicio:.2f} segundos")
    return suma_parcial

def suma_factoriales_paralelo(n, num_workers=4):
    """Calcula la suma de factoriales usando ProcessPool"""
    rango_por_worker = n // num_workers
    tareas = []
    
    for i in range(num_workers):
        inicio = i * rango_por_worker + 1
        if i == num_workers - 1:
            fin = n
        else:
            fin = (i + 1) * rango_por_worker
        
        task_name = f"Task {chr(65 + i)}"
        tareas.append((inicio, fin, task_name))
    
    print("Rangos asignados:")
    print("-" * 50)
    for inicio, fin, task_name in tareas:
        print(f"{task_name}: [{inicio:,}, {fin:,}]")
    print("-" * 50)
    print()
    
    suma_total = 0
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        resultados = executor.map(suma_factoriales_rango, tareas)
        
        for resultado in resultados:
            suma_total += resultado
    
    return suma_total

if __name__ == "__main__":
    N = 1000000
    num_workers = 4
    
    print(f"Calculando la suma de factoriales de 1 a {N:,} usando {num_workers} workers (ProcessPool)")
    print("=" * 50)
    print()
    
    inicio = time.time()
    resultado = suma_factoriales_paralelo(N, num_workers)
    fin = time.time()
    
    tiempo_transcurrido = fin - inicio
    
    print()
    print("=" * 50)
    print(f"Tiempo de ejecución total: {tiempo_transcurrido:.6f} segundos")
    print("-" * 50)
    print(f"Número de dígitos del resultado: {len(str(resultado)):,}")
    print("=" * 50)