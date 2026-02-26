"""
FilterFactory - Patrón Factory para crear filtros dinámicamente.

Permite crear filtros desde strings, configuraciones JSON, o CLI args.
Facilita la creación dinámica sin necesidad de importar cada clase.
"""

from typing import Dict, Any, List, Optional
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from filters import (
    BaseFilter,
    BlurFilter,
    BrightnessFilter,
    EdgesFilter,
    GrayscaleFilter
)
from .filter_pipeline import FilterPipeline


class FilterFactory:
    """
    Factory para crear filtros dinámicamente.
    
    Permite crear filtros sin importar explícitamente las clases,
    útil para:
    - APIs que reciben configuración JSON
    - CLI que acepta comandos de usuario
    - Sistemas configurables
    - Testing dinámico
    
    Ejemplo:
        factory = FilterFactory()
        
        # Crear filtro individual
        blur = factory.create('blur', radius=5)
        
        # Crear pipeline desde configuración
        config = [
            {'type': 'blur', 'radius': 3},
            {'type': 'brightness', 'factor': 1.5}
        ]
        pipeline = factory.create_pipeline(config)
    """
    
    # Registro de filtros disponibles
    # Mapea nombre → clase
    _FILTER_REGISTRY: Dict[str, type] = {
        'blur': BlurFilter,
        'brightness': BrightnessFilter,
        'edges': EdgesFilter,
        'grayscale': GrayscaleFilter,
        'gray': GrayscaleFilter,  # Alias
    }
    
    def __init__(self):
        """Inicializa la factory."""
        pass
    
    def create(self, filter_type: str, **kwargs) -> BaseFilter:
        """
        Crea un filtro por su nombre.
        
        Args:
            filter_type: Nombre del filtro ('blur', 'brightness', etc.)
            **kwargs: Parámetros específicos del filtro
            
        Returns:
            BaseFilter: Instancia del filtro creado
            
        Raises:
            ValueError: Si el tipo de filtro no existe
            TypeError: Si los parámetros son inválidos
            
        Ejemplo:
            blur = factory.create('blur', radius=5)
            bright = factory.create('brightness', factor=1.5)
            edges = factory.create('edges')
        """
        filter_type_lower = filter_type.lower()
        
        if filter_type_lower not in self._FILTER_REGISTRY:
            available = ', '.join(self._FILTER_REGISTRY.keys())
            raise ValueError(
                f"Filtro '{filter_type}' no encontrado. "
                f"Disponibles: {available}"
            )
        
        filter_class = self._FILTER_REGISTRY[filter_type_lower]
        
        try:
            return filter_class(**kwargs)
        except TypeError as e:
            raise TypeError(
                f"Error creando filtro '{filter_type}' con parámetros {kwargs}: {e}"
            )
    
    def create_from_config(self, config: Dict[str, Any]) -> BaseFilter:
        """
        Crea un filtro desde un diccionario de configuración.
        
        Args:
            config: Diccionario con 'type' y parámetros opcionales
                   Ejemplo: {'type': 'blur', 'radius': 5}
            
        Returns:
            BaseFilter: Filtro creado
            
        Ejemplo:
            config = {'type': 'blur', 'radius': 3}
            blur = factory.create_from_config(config)
        """
        if 'type' not in config:
            raise ValueError("La configuración debe incluir el campo 'type'")
        
        filter_type = config['type']
        params = {k: v for k, v in config.items() if k != 'type'}
        
        return self.create(filter_type, **params)
    
    def create_pipeline(
        self, 
        configs: List[Dict[str, Any]],
        **pipeline_kwargs
    ) -> FilterPipeline:
        """
        Crea un pipeline completo desde una lista de configuraciones.
        
        Args:
            configs: Lista de configuraciones de filtros
            **pipeline_kwargs: Parámetros para el pipeline
            
        Returns:
            FilterPipeline: Pipeline con todos los filtros
            
        Ejemplo:
            configs = [
                {'type': 'blur', 'radius': 2},
                {'type': 'brightness', 'factor': 1.5},
                {'type': 'edges'}
            ]
            pipeline = factory.create_pipeline(configs)
        """
        filters = []
        
        for i, config in enumerate(configs):
            try:
                filter_obj = self.create_from_config(config)
                filters.append(filter_obj)
            except Exception as e:
                raise ValueError(
                    f"Error creando filtro {i} ({config.get('type', 'unknown')}): {e}"
                )
        
        return FilterPipeline(filters, **pipeline_kwargs)
    
    @classmethod
    def register_filter(cls, name: str, filter_class: type):
        """
        Registra un nuevo filtro personalizado.
        
        Args:
            name: Nombre para identificar el filtro
            filter_class: Clase del filtro (debe heredar de BaseFilter)
            
        Ejemplo:
            class MiFiltro(BaseFilter):
                def apply(self, image):
                    return image.rotate(90)
            
            FilterFactory.register_filter('rotate90', MiFiltro)
            
            # Ahora se puede usar
            factory = FilterFactory()
            rotate = factory.create('rotate90')
        """
        if not issubclass(filter_class, BaseFilter):
            raise TypeError(
                f"La clase debe heredar de BaseFilter, recibido: {filter_class}"
            )
        
        cls._FILTER_REGISTRY[name.lower()] = filter_class
    
    @classmethod
    def get_available_filters(cls) -> List[str]:
        """
        Obtiene la lista de filtros disponibles.
        
        Returns:
            List[str]: Nombres de filtros registrados
        """
        return list(cls._FILTER_REGISTRY.keys())
    
    def __repr__(self) -> str:
        """Representación en string."""
        available = ', '.join(self.get_available_filters())
        return f"FilterFactory(available={available})"


# Ejemplo de uso
if __name__ == "__main__":
    print("🏭 Ejemplo de uso de FilterFactory")
    print("=" * 60)
    
    factory = FilterFactory()
    
    print(f"\n📋 Filtros disponibles: {factory.get_available_filters()}")
    
    print("\n💡 Ejemplo 1: Crear filtro individual")
    print("""
    factory = FilterFactory()
    blur = factory.create('blur', radius=5)
    result = blur.apply(image)
    """)
    
    print("\n💡 Ejemplo 2: Desde configuración JSON")
    print("""
    config = {
        'type': 'brightness',
        'factor': 1.5
    }
    filter = factory.create_from_config(config)
    """)
    
    print("\n💡 Ejemplo 3: Pipeline completo desde config")
    print("""
    pipeline_config = [
        {'type': 'grayscale'},
        {'type': 'blur', 'radius': 3},
        {'type': 'brightness', 'factor': 1.2}
    ]
    
    pipeline = factory.create_pipeline(pipeline_config)
    result, stats = pipeline.apply(image)
    """)
    
    print("\n💡 Ejemplo 4: Registrar filtro personalizado")
    print("""
    class RotateFilter(BaseFilter):
        def __init__(self, angle=90):
            self.angle = angle
        
        def apply(self, image):
            return image.rotate(self.angle)
    
    # Registrar
    FilterFactory.register_filter('rotate', RotateFilter)
    
    # Usar
    rotate = factory.create('rotate', angle=45)
    """)
    
    print("\n🎯 Casos de uso:")
    print("""
    ✓ APIs REST que reciben configuración JSON
    ✓ CLIs que aceptan comandos de usuario
    ✓ Sistemas configurables via archivos
    ✓ Testing dinámico de filtros
    ✓ Plugins/extensiones de usuario
    """)

