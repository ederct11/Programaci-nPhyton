from PIL import Image
from .base_filter import BaseFilter

class GrayScaleFilter(BaseFilter):
    
    def apply(self, image: Image.Image) -> Image.Image:
        return image.convert('L')
    
    def __repr__(self) -> str:
        """Representación en string del filtro."""
        return f"GrayScaleFilter()"