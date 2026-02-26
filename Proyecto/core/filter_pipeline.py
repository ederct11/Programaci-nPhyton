"""
FilterPipeline - Cadena de filtros para procesamiento secuencial.

Permite aplicar múltiples filtros en secuencia, midiendo tiempos
y manejando errores de manera elegante.
"""

import time
from typing import List, Dict, Tuple, Optional
from PIL import Image
import sys
import os

# Agregar el directorio padre al path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from filters.base_filter import BaseFilter


class FilterPipeline:
    """
    Pipeline que aplica múltiples filtros en secuencia.
    
    Características:
    - Aplica filtros en el orden especificado
    - Mide tiempo de ejecución de cada filtro
    - Maneja errores (puede continuar o detenerse)
    - Puede guardar imágenes intermedias
    - Retorna estadísticas detalladas
    
    Attributes:
        filters (List[BaseFilter]): Lista de filtros a aplicar
        stop_on_error (bool): Si True, detiene al primer error
        save_intermediate (bool): Si True, guarda imágenes intermedias
        
    Ejemplo:
        pipeline = FilterPipeline([
            BlurFilter(radius=3),
            BrightnessFilter(factor=1.5),
            EdgesFilter()
        ])
        
        result, stats = pipeline.apply(image)
        print(f"Tiempo total: {stats['total_time']:.3f}s")
    """
    
    def __init__(
        self, 
        filters: List[BaseFilter],
        stop_on_error: bool = True,
        save_intermediate: bool = False
    ):
        """
        Inicializa el pipeline con una lista de filtros.
        
        Args:
            filters: Lista de filtros a aplicar en orden
            stop_on_error: Si True, detiene al primer error
            save_intermediate: Si True, guarda imágenes intermedias
        """
        if not filters:
            raise ValueError("El pipeline debe tener al menos un filtro")
        
        # Validar que todos sean filtros válidos
        for i, f in enumerate(filters):
            if not isinstance(f, BaseFilter):
                raise TypeError(
                    f"Filtro {i} no es instancia de BaseFilter: {type(f)}"
                )
        
        self.filters = filters
        self.stop_on_error = stop_on_error
        self.save_intermediate = save_intermediate
    
    def apply(
        self, 
        image: Image.Image,
        output_dir: Optional[str] = None
    ) -> Tuple[Optional[Image.Image], Dict]:
        """
        Aplica todos los filtros en secuencia.
        
        Args:
            image: Imagen de entrada
            output_dir: Directorio para guardar imágenes intermedias
            
        Returns:
            Tuple[Image, Dict]: (imagen procesada, estadísticas)
            
        Estadísticas retornadas:
            {
                'total_time': float,
                'filters': [
                    {
                        'name': str,
                        'index': int,
                        'time': float,
                        'status': 'success' | 'failed',
                        'error': str (opcional)
                    },
                    ...
                ],
                'successful': int,
                'failed': int
            }
        """
        start_time = time.time()
        
        result_image = image.copy()  # Trabajar con copia
        filter_stats = []
        successful_count = 0
        failed_count = 0
        
        # Aplicar cada filtro
        for i, filter_obj in enumerate(self.filters):
            filter_name = filter_obj.__class__.__name__
            filter_start = time.time()
            
            try:
                # Aplicar el filtro
                result_image = filter_obj.apply(result_image)
                filter_time = time.time() - filter_start
                
                # Registrar éxito
                filter_stats.append({
                    'name': filter_name,
                    'index': i,
                    'time': filter_time,
                    'status': 'success'
                })
                successful_count += 1
                
                # Guardar imagen intermedia si se solicita
                if self.save_intermediate and output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    intermediate_path = os.path.join(
                        output_dir,
                        f"step_{i:02d}_{filter_name}.jpg"
                    )
                    result_image.save(intermediate_path)
                
            except Exception as e:
                filter_time = time.time() - filter_start
                
                # Registrar error
                filter_stats.append({
                    'name': filter_name,
                    'index': i,
                    'time': filter_time,
                    'status': 'failed',
                    'error': str(e)
                })
                failed_count += 1
                
                # Decidir si continuar o detenerse
                if self.stop_on_error:
                    break
        
        total_time = time.time() - start_time
        
        # Compilar estadísticas
        stats = {
            'total_time': total_time,
            'filters': filter_stats,
            'successful': successful_count,
            'failed': failed_count,
            'total_filters': len(self.filters)
        }
        
        # Si todos fallaron, retornar None
        if successful_count == 0:
            return None, stats
        
        return result_image, stats
    
    def add_filter(self, filter_obj: BaseFilter):
        """
        Añade un filtro al final del pipeline.
        
        Args:
            filter_obj: Filtro a añadir
        """
        if not isinstance(filter_obj, BaseFilter):
            raise TypeError(f"Debe ser BaseFilter, recibido: {type(filter_obj)}")
        
        self.filters.append(filter_obj)
    
    def remove_filter(self, index: int):
        """
        Elimina un filtro por su índice.
        
        Args:
            index: Índice del filtro a eliminar
        """
        if 0 <= index < len(self.filters):
            removed = self.filters.pop(index)
            return removed
        else:
            raise IndexError(f"Índice {index} fuera de rango (0-{len(self.filters)-1})")
    
    def get_filter_names(self) -> List[str]:
        """
        Obtiene los nombres de todos los filtros en el pipeline.
        
        Returns:
            List[str]: Lista de nombres de filtros
        """
        return [f.__class__.__name__ for f in self.filters]
    
    def __repr__(self) -> str:
        """Representación en string del pipeline."""
        filter_names = " → ".join(self.get_filter_names())
        return f"FilterPipeline({filter_names})"
    
    def __len__(self) -> int:
        """Número de filtros en el pipeline."""
        return len(self.filters)


# Ejemplo de uso
if __name__ == "__main__":
    print("🔗 Ejemplo de uso de FilterPipeline")
    print("=" * 60)
    
    print("""
    El FilterPipeline permite aplicar múltiples filtros en secuencia:
    
    Imagen Original
         ↓
    [Filtro 1: Blur]
         ↓
    [Filtro 2: Brightness]
         ↓
    [Filtro 3: Edges]
         ↓
    Imagen Final
    
    Ventajas:
    ✓ Código más limpio y expresivo
    ✓ Medición automática de tiempos
    ✓ Manejo robusto de errores
    ✓ Fácil de modificar y reutilizar
    """)
    
    print("\n💡 Ejemplo de código:")
    print("""
    from PIL import Image
    from core import FilterPipeline
    from filters import BlurFilter, BrightnessFilter, EdgesFilter
    
    # Crear pipeline
    pipeline = FilterPipeline([
        BlurFilter(radius=2),
        BrightnessFilter(factor=1.3),
        EdgesFilter()
    ])
    
    # Aplicar
    image = Image.open('photo.jpg')
    result, stats = pipeline.apply(image)
    
    # Ver estadísticas
    print(f"Tiempo total: {stats['total_time']:.3f}s")
    for f in stats['filters']:
        print(f"  {f['name']}: {f['time']:.3f}s - {f['status']}")
    
    # Guardar resultado
    result.save('processed.jpg')
    """)

