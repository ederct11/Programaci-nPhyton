"""
Filtro de escala de grises (Grayscale).

Convierte imágenes en color a escala de grises usando luminancia.
"""

from PIL import Image
from .base_filter import BaseFilter


class GrayscaleFilter(BaseFilter):
    """
    Filtro que convierte una imagen a escala de grises.
    
    Utiliza el modo 'L' (Luminance) de PIL, que convierte colores RGB
    a valores de gris usando una fórmula ponderada que refleja cómo
    el ojo humano percibe el brillo:
    
    Gray = 0.299×R + 0.587×G + 0.114×B
    
    El ojo humano es más sensible al verde, por eso tiene más peso.
    
    Ejemplo:
        gray = GrayscaleFilter()
        result = gray.apply(color_image)
    """
    
    def apply(self, image: Image.Image) -> Image.Image:
        """
        Convierte la imagen a escala de grises.
        
        Args:
            image (PIL.Image.Image): Imagen de entrada (cualquier modo)
            
        Returns:
            PIL.Image.Image: Imagen en escala de grises (modo 'L')
        """
        # convert('L') usa la fórmula de luminancia estándar
        # L = Luminance (percepción de brillo por el ojo humano)
        return image.convert('L')
    
    def __repr__(self) -> str:
        """Representación en string del filtro."""
        return "GrayscaleFilter()"


# Ejemplo de uso
if __name__ == "__main__":
    print("⚫⚪ Ejemplo de uso de GrayscaleFilter")
    print("-" * 50)
    
    print("""
    El modo 'L' representa Luminance (Luminancia).
    
    ¿Por qué 'L'?
    -------------
    PIL usa esta letra porque la luminancia es la medida
    de brillo percibido por el ojo humano, diferente del
    brillo físico de la luz.
    
    Fórmula estándar (ITU-R 601-2):
    Gray = 0.299×R + 0.587×G + 0.114×B
    
    Ejemplo con colores puros:
    - Rojo   (255, 0, 0)   → Gray: 76  (gris oscuro)
    - Verde  (0, 255, 0)   → Gray: 150 (gris claro) ← ¡más brillante!
    - Azul   (0, 0, 255)   → Gray: 29  (gris muy oscuro)
    
    El verde se ve más brillante porque el ojo humano
    es más sensible a ese color.
    """)
    
    print("\n💡 Para usar este filtro:")
    print("""
    from PIL import Image
    from filters.grayscale_filter import GrayscaleFilter
    
    image = Image.open('photo.jpg')
    gray_filter = GrayscaleFilter()
    result = gray_filter.apply(image)
    result.save('photo_gray.jpg')
    """)

