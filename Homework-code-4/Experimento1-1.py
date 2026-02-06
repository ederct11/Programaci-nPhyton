import time
import random

def procedimiento_bloqueo(numero):
    inicio = time.time()
    
    time.sleep(1)
    
    tiempo_aleatorio = random.uniform(0, 0.5)
    time.sleep(tiempo_aleatorio)
    
    fin = time.time()
    tiempo_ejecucion = fin - inicio
    
    print(f"[Ejecución {numero}] Log: Esperando {tiempo_ejecucion:.4f} segundos")
    
    return tiempo_ejecucion

print("=" * 60)
print("EJECUCIÓN SECUENCIAL - 20 ITERACIONES")
print("=" * 60)
print()

tiempo_inicio_total = time.time()

for i in range(1, 21):
    procedimiento_bloqueo(i)

tiempo_fin_total = time.time()
tiempo_total = tiempo_fin_total - tiempo_inicio_total

print()
print("=" * 60)
print(f"TIEMPO TOTAL DE EJECUCIÓN: {tiempo_total:.4f} segundos")
print("=" * 60)