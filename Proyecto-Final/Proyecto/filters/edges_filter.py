"""
Filtro de detección de bordes.

Este filtro identifica los bordes en una imagen, útil para:
- Computer vision
- Análisis de formas
- Efectos artísticos estilo "sketch"
"""

from PIL import Image, ImageFilter
from .base_filter import BaseFilter


class EdgesFilter(BaseFilter):
    """
    Filtro que detecta bordes en una imagen.
    
    La detección de bordes identifica áreas donde hay cambios
    bruscos en el color o intensidad. Es útil para:
    
    - Segmentación de imágenes
    - Reconocimiento de objetos
    - Efectos artísticos (dibujo a lápiz)
    - Análisis de formas y contornos
    
    El filtro utiliza un operador de gradiente para encontrar
    cambios rápidos en la intensidad de los píxeles.
    
    Nota:
        Este filtro no tiene parámetros configurables.
        El resultado es una imagen en escala de grises donde
        los bordes aparecen en blanco y el resto en negro.
    
    Ejemplo:
        edges = EdgesFilter()
        result = edges.apply(image)
        result.save('bordes.jpg')
    """
    
    def __init__(self):
        """
        Inicializa el filtro de detección de bordes.
        
        Este filtro no requiere parámetros.
        """
        pass
    
    def apply(self, image: Image.Image) -> Image.Image:
        """
        Aplica el filtro de detección de bordes a la imagen.
        
        El algoritmo:
        1. Convierte la imagen a escala de grises (si es necesario)
        2. Aplica un operador de gradiente para detectar cambios
        3. Resalta las áreas donde hay cambios bruscos (bordes)
        
        Args:
            image (PIL.Image.Image): Imagen de entrada
            
        Returns:
            PIL.Image.Image: Imagen con bordes detectados
                           (típicamente en escala de grises)
        """
        # ImageFilter.FIND_EDGES es un filtro predefinido de PIL
        # que implementa detección de bordes usando convolución
        return image.filter(ImageFilter.FIND_EDGES)
    
    def __repr__(self) -> str:
        """Representación en string del filtro."""
        return "EdgesFilter()"


# Ejemplo de uso directo
if __name__ == "__main__":
    print("🎨 Ejemplo de uso de EdgesFilter")
    print("-" * 50)
    
    # Crear instancia del filtro
    edges_filter = EdgesFilter()
    print(f"Filtro creado: {edges_filter}")
    
    print("\n📖 ¿Qué hace este filtro?")
    print("""
    El filtro de detección de bordes identifica:
    
    ✓ Contornos de objetos
    ✓ Líneas y formas
    ✓ Cambios de color bruscos
    ✓ Transiciones de luz a sombra
    
    Resultado:
    - Fondo: Negro (sin bordes)
    - Bordes: Blanco (cambios detectados)
    """)
    
    print("\n💡 Para usar este filtro en tu código:")
    print("""
    from PIL import Image
    from filters.edges_filter import EdgesFilter
    
    # Cargar imagen
    image = Image.open('foto.jpg')
    
    # Detectar bordes
    edges = EdgesFilter()
    result = edges.apply(image)
    
    # Guardar resultado
    result.save('bordes_detectados.jpg')
    """)
    
    print("\n🔬 Aplicaciones prácticas:")
    print("""
    1. Computer Vision:
       - Reconocimiento de objetos
       - Seguimiento de movimiento
       - Análisis de formas
    
    2. Efectos Artísticos:
       - Efecto "dibujo a lápiz"
       - Estilo cómic/manga
       - Arte generativo
    
    3. Procesamiento:
       - Segmentación de imágenes
       - Mejora de contraste
       - Preparación para OCR
    """)

