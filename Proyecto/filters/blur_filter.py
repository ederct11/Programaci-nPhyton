"""
Filtro de desenfoque (blur) usando desenfoque gaussiano.

Este filtro suaviza la imagen, útil para:
- Reducir ruido
- Crear efectos artísticos
- Preparar imágenes para otros procesamientos
"""

from PIL import Image, ImageFilter
from .base_filter import BaseFilter


class BlurFilter(BaseFilter):
    """
    Filtro que aplica desenfoque gaussiano a una imagen.
    
    El desenfoque gaussiano es una técnica que suaviza la imagen
    promediando los píxeles con sus vecinos, usando una distribución
    gaussiana para determinar los pesos.
    
    Attributes:
        radius (int): Radio del desenfoque. Valores más altos = más desenfoque
                     Rango típico: 1-10
                     Default: 2
    
    Ejemplo:
        # Desenfoque suave
        blur = BlurFilter(radius=2)
        result = blur.apply(image)
        
        # Desenfoque fuerte
        blur = BlurFilter(radius=10)
        result = blur.apply(image)
    """
    
    def __init__(self, radius: int = 2):
        """
        Inicializa el filtro de desenfoque.
        
        Args:
            radius (int): Radio del desenfoque gaussiano
                         Valores típicos: 1-10
        """
        if radius < 0:
            raise ValueError(f"El radio debe ser positivo, se recibió: {radius}")
        
        self.radius = radius
    
    def apply(self, image: Image.Image) -> Image.Image:
        """
        Aplica el desenfoque gaussiano a la imagen.
        
        Args:
            image (PIL.Image.Image): Imagen de entrada
            
        Returns:
            PIL.Image.Image: Imagen desenfocada
        """
        # ImageFilter.GaussianBlur es un filtro predefinido de PIL
        # que implementa el desenfoque gaussiano eficientemente
        return image.filter(ImageFilter.GaussianBlur(radius=self.radius))
    
    def __repr__(self) -> str:
        """Representación en string del filtro."""
        return f"BlurFilter(radius={self.radius})"


# Ejemplo de uso directo (si ejecutas este archivo)
if __name__ == "__main__":
    print("📸 Ejemplo de uso de BlurFilter")
    print("-" * 50)
    
    # Crear instancia del filtro
    blur_filter = BlurFilter(radius=5)
    print(f"Filtro creado: {blur_filter}")
    
    # Simular aplicación (necesitarías una imagen real)
    print("\n💡 Para usar este filtro en tu código:")
    print("""
    from PIL import Image
    from filters.blur_filter import BlurFilter
    
    # Cargar imagen
    image = Image.open('ruta/a/imagen.jpg')
    
    # Crear filtro
    blur = BlurFilter(radius=3)
    
    # Aplicar filtro
    result = blur.apply(image)
    
    # Guardar resultado
    result.save('imagen_desenfocada.jpg')
    """)

