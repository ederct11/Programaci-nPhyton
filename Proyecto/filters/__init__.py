"""
Módulo de filtros para procesamiento de imágenes.

Este módulo contiene:
- BaseFilter: Clase base abstracta para todos los filtros
- BlurFilter: Filtro de desenfoque gaussiano
- BrightnessFilter: Filtro de ajuste de brillo
- EdgesFilter: Filtro de detección de bordes
- GrayscaleFilter: Filtro de conversión a escala de grises

Uso:
    from filters import BlurFilter
    
    blur = BlurFilter(radius=3)
    result = blur.apply(image)
"""

from .base_filter import BaseFilter
from .blur_filter import BlurFilter
from .brightness_filter import BrightnessFilter
from .edges_filter import EdgesFilter
from .grayscale_filter import GrayscaleFilter

__all__ = [
    'BaseFilter',
    'BlurFilter',
    'BrightnessFilter',
    'EdgesFilter',
    'GrayscaleFilter'
]

