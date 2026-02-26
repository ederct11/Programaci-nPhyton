"""
Clase base abstracta para todos los filtros de imagen.

Esta clase define la interfaz que todos los filtros deben implementar.
Usar una clase base nos permite:
1. Garantizar que todos los filtros tengan el método 'apply'
2. Facilitar la composición de filtros
3. Permitir polimorfismo (tratar todos los filtros de la misma manera)
"""

from abc import ABC, abstractmethod
from PIL import Image


class BaseFilter(ABC):
    """
    Clase base abstracta para filtros de imagen.
    
    Todos los filtros deben heredar de esta clase e implementar
    el método 'apply'.
    
    Ejemplo:
        class MiFiltro(BaseFilter):
            def apply(self, image):
                # Lógica del filtro aquí
                return image_modificada
    """
    
    @abstractmethod
    def apply(self, image: Image.Image) -> Image.Image:
        """
        Aplica el filtro a una imagen.
        
        Args:
            image (PIL.Image.Image): Imagen de entrada
            
        Returns:
            PIL.Image.Image: Imagen con el filtro aplicado
            
        Raises:
            NotImplementedError: Si el método no está implementado
        """
        raise NotImplementedError(
            f"La clase {self.__class__.__name__} debe implementar el método 'apply'"
        )
    
    def __repr__(self) -> str:
        """
        Representación en string del filtro.
        
        Returns:
            str: Nombre de la clase del filtro
        """
        return f"{self.__class__.__name__}()"

