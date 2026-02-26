"""
Filtro de ajuste de brillo.

Este filtro modifica el brillo (luminosidad) de una imagen,
haciéndola más clara u oscura.
"""

from PIL import Image, ImageEnhance
from .base_filter import BaseFilter


class BrightnessFilter(BaseFilter):
    """
    Filtro que ajusta el brillo de una imagen.
    
    Utiliza ImageEnhance.Brightness de PIL para modificar
    la luminosidad de todos los píxeles de manera proporcional.
    
    Attributes:
        factor (float): Factor de multiplicación del brillo
                       - factor < 1.0: Imagen más oscura
                       - factor = 1.0: Sin cambio
                       - factor > 1.0: Imagen más brillante
                       
                       Ejemplos:
                       - 0.5 = 50% más oscura
                       - 1.0 = Sin cambio
                       - 1.5 = 50% más brillante
                       - 2.0 = El doble de brillante
    
    Ejemplo:
        # Hacer imagen más brillante
        bright = BrightnessFilter(factor=1.5)
        result = bright.apply(image)
        
        # Hacer imagen más oscura
        dark = BrightnessFilter(factor=0.5)
        result = dark.apply(image)
    """
    
    def __init__(self, factor: float = 1.5):
        """
        Inicializa el filtro de brillo.
        
        Args:
            factor (float): Factor de multiplicación del brillo
                          Rango recomendado: 0.1 - 3.0
        """
        if factor < 0:
            raise ValueError(f"El factor debe ser positivo, se recibió: {factor}")
        
        if factor > 5.0:
            print(f"⚠️  Advertencia: factor={factor} es muy alto, puede causar sobreexposición")
        
        self.factor = factor
    
    def apply(self, image: Image.Image) -> Image.Image:
        """
        Aplica el ajuste de brillo a la imagen.
        
        Args:
            image (PIL.Image.Image): Imagen de entrada
            
        Returns:
            PIL.Image.Image: Imagen con brillo ajustado
        """
        # ImageEnhance.Brightness es una clase de PIL que permite
        # ajustar el brillo de manera eficiente
        enhancer = ImageEnhance.Brightness(image)
        
        # El método enhance() aplica el factor multiplicador
        # a cada píxel de la imagen
        return enhancer.enhance(self.factor)
    
    def __repr__(self) -> str:
        """Representación en string del filtro."""
        return f"BrightnessFilter(factor={self.factor})"


# Ejemplo de uso directo
if __name__ == "__main__":
    print("✨ Ejemplo de uso de BrightnessFilter")
    print("-" * 50)
    
    # Ejemplos de diferentes factores
    examples = [
        (0.3, "Muy oscura (30%)"),
        (0.7, "Oscura (70%)"),
        (1.0, "Sin cambio (100%)"),
        (1.5, "Brillante (150%)"),
        (2.0, "Muy brillante (200%)"),
    ]
    
    print("\n📊 Ejemplos de factores de brillo:")
    for factor, description in examples:
        filter_obj = BrightnessFilter(factor=factor)
        print(f"  {filter_obj} → {description}")
    
    print("\n💡 Para usar este filtro en tu código:")
    print("""
    from PIL import Image
    from filters.brightness_filter import BrightnessFilter
    
    # Cargar imagen
    image = Image.open('ruta/a/imagen.jpg')
    
    # Hacer imagen más brillante
    bright_filter = BrightnessFilter(factor=1.5)
    result = bright_filter.apply(image)
    result.save('imagen_brillante.jpg')
    
    # Hacer imagen más oscura
    dark_filter = BrightnessFilter(factor=0.5)
    result = dark_filter.apply(image)
    result.save('imagen_oscura.jpg')
    """)

