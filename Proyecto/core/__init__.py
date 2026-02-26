"""
Módulo core para procesamiento avanzado de imágenes.

Este módulo contiene:
- FilterPipeline: Cadena de filtros
- FilterFactory: Creación dinámica de filtros
- BatchProcessor: Procesamiento en lote

Uso:
    from core import FilterPipeline, FilterFactory
    
    factory = FilterFactory()
    pipeline = factory.create_pipeline([
        {'type': 'blur', 'radius': 3},
        {'type': 'brightness', 'factor': 1.5}
    ])
    
    result = pipeline.apply(image)
"""

from .filter_pipeline import FilterPipeline
from .filter_factory import FilterFactory
from .batch_processor import BatchProcessor

__all__ = [
    'FilterPipeline',
    'FilterFactory',
    'BatchProcessor',
]

