import time
import sys

sys.set_int_max_str_digits(0)

def factorial(n):
    if n == 0 or n == 1:
        return 1
    resultado = 1
    for i in range(2, n + 1):
        resultado *= i
    return resultado

def suma_factoriales_secuencial(n):
    suma_total = 0
    for i in range(1, n + 1):
        suma_total += factorial(i)
    return suma_total

if __name__ == "__main__":
    N = 10000
    
    print(f"Calculando la suma de factoriales de 1 a {N}...")
    print("-" * 50)
    
    inicio = time.time()
    resultado = suma_factoriales_secuencial(N)
    fin = time.time()
    
    tiempo_transcurrido = fin - inicio
    
    print(f"Tiempo de ejecución: {tiempo_transcurrido:.6f} segundos")
    print("-" * 50)
    
    print(f"\nNúmero de dígitos del resultado: {len(str(resultado))}")