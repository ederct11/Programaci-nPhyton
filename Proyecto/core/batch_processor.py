"""
BatchProcessor - Procesamiento en lote de múltiples imágenes.

Permite procesar carpetas completas de imágenes con el mismo pipeline,
mostrando progreso y generando reportes detallados.
"""

import os
import time
from typing import Dict, List, Optional
from PIL import Image
import sys

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .filter_pipeline import FilterPipeline


class BatchProcessor:
    """
    Procesador en lote para múltiples imágenes.
    
    Características:
    - Procesa carpetas completas de imágenes
    - Soporta múltiples formatos (JPG, PNG, JPEG, BMP)
    - Muestra progreso en tiempo real
    - Maneja errores gracefully
    - Genera reporte detallado
    - Preserva estructura de carpetas (opcional)
    
    Attributes:
        input_dir (str): Directorio de entrada con imágenes
        output_dir (str): Directorio de salida
        pipeline (FilterPipeline): Pipeline a aplicar
        supported_formats (List[str]): Formatos de imagen soportados
        
    Ejemplo:
        processor = BatchProcessor(
            input_dir='images/',
            output_dir='output/batch/',
            pipeline=my_pipeline
        )
        
        results = processor.process_all()
        print(f"Procesadas: {results['successful']}/{results['total']}")
    """
    
    SUPPORTED_FORMATS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    
    def __init__(
        self,
        input_dir: str,
        output_dir: str,
        pipeline: FilterPipeline,
        recursive: bool = False,
        preserve_structure: bool = False
    ):
        """
        Inicializa el procesador en lote.
        
        Args:
            input_dir: Carpeta con imágenes de entrada
            output_dir: Carpeta para guardar resultados
            pipeline: Pipeline de filtros a aplicar
            recursive: Si True, busca imágenes en subcarpetas
            preserve_structure: Si True, preserva estructura de carpetas
        """
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Directorio de entrada no existe: {input_dir}")
        
        if not isinstance(pipeline, FilterPipeline):
            raise TypeError(f"pipeline debe ser FilterPipeline, recibido: {type(pipeline)}")
        
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.pipeline = pipeline
        self.recursive = recursive
        self.preserve_structure = preserve_structure
        
        # Crear directorio de salida
        os.makedirs(output_dir, exist_ok=True)
    
    def find_images(self) -> List[str]:
        """
        Encuentra todas las imágenes en el directorio de entrada.
        
        Returns:
            List[str]: Lista de rutas de imágenes encontradas
        """
        images = []
        
        if self.recursive:
            for root, _, files in os.walk(self.input_dir):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in self.SUPPORTED_FORMATS):
                        images.append(os.path.join(root, file))
        else:
            for file in os.listdir(self.input_dir):
                if any(file.lower().endswith(ext) for ext in self.SUPPORTED_FORMATS):
                    images.append(os.path.join(self.input_dir, file))
        
        return sorted(images)
    
    def process_image(self, input_path: str) -> Dict:
        """
        Procesa una imagen individual.
        
        Args:
            input_path: Ruta de la imagen de entrada
            
        Returns:
            Dict: Resultado del procesamiento con estadísticas
        """
        start_time = time.time()
        
        try:
            # Cargar imagen
            image = Image.open(input_path)
            original_size = image.size
            
            # Aplicar pipeline
            result, stats = self.pipeline.apply(image)
            
            if result is None:
                return {
                    'input_path': input_path,
                    'status': 'failed',
                    'error': 'Pipeline failed completely',
                    'time': time.time() - start_time
                }
            
            # Determinar ruta de salida
            relative_path = os.path.relpath(input_path, self.input_dir)
            
            if self.preserve_structure:
                output_path = os.path.join(self.output_dir, relative_path)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            else:
                filename = os.path.basename(input_path)
                output_path = os.path.join(self.output_dir, filename)
            
            # Guardar resultado
            result.save(output_path, quality=95)
            
            processing_time = time.time() - start_time
            
            return {
                'input_path': input_path,
                'output_path': output_path,
                'status': 'success',
                'original_size': original_size,
                'time': processing_time,
                'pipeline_stats': stats
            }
            
        except Exception as e:
            return {
                'input_path': input_path,
                'status': 'failed',
                'error': str(e),
                'time': time.time() - start_time
            }
    
    def process_all(self, verbose: bool = True) -> Dict:
        """
        Procesa todas las imágenes encontradas.
        
        Args:
            verbose: Si True, muestra progreso en consola
            
        Returns:
            Dict: Reporte completo con estadísticas
        """
        start_time = time.time()
        
        # Encontrar imágenes
        images = self.find_images()
        total_images = len(images)
        
        if total_images == 0:
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'results': [],
                'total_time': 0,
                'error': 'No se encontraron imágenes'
            }
        
        if verbose:
            print(f"🔍 Encontradas {total_images} imágenes")
            print(f"🔄 Procesando con pipeline: {self.pipeline}")
            print("-" * 60)
        
        results = []
        successful = 0
        failed = 0
        
        # Procesar cada imagen
        for i, image_path in enumerate(images, 1):
            if verbose:
                filename = os.path.basename(image_path)
                print(f"\n[{i}/{total_images}] {filename}")
            
            result = self.process_image(image_path)
            results.append(result)
            
            if result['status'] == 'success':
                successful += 1
                if verbose:
                    print(f"   ✅ Procesada en {result['time']:.3f}s")
            else:
                failed += 1
                if verbose:
                    print(f"   ❌ Error: {result.get('error', 'Unknown')}")
        
        total_time = time.time() - start_time
        
        # Compilar reporte
        report = {
            'total': total_images,
            'successful': successful,
            'failed': failed,
            'results': results,
            'total_time': total_time,
            'avg_time': total_time / total_images if total_images > 0 else 0,
            'pipeline': str(self.pipeline)
        }
        
        if verbose:
            print("\n" + "=" * 60)
            print("📊 REPORTE FINAL")
            print("=" * 60)
            print(f"✅ Exitosas: {successful}/{total_images}")
            print(f"❌ Fallidas: {failed}/{total_images}")
            print(f"⏱️  Tiempo total: {total_time:.2f}s")
            print(f"⏱️  Tiempo promedio: {report['avg_time']:.2f}s por imagen")
            print("=" * 60)
        
        return report
    
    def __repr__(self) -> str:
        """Representación en string."""
        return (
            f"BatchProcessor("
            f"input={self.input_dir}, "
            f"output={self.output_dir}, "
            f"pipeline={self.pipeline})"
        )


# Ejemplo de uso
if __name__ == "__main__":
    print("📦 Ejemplo de uso de BatchProcessor")
    print("=" * 60)
    
    print("""
    El BatchProcessor facilita el procesamiento de múltiples imágenes:
    
    Entrada:
    images/
      ├── photo1.jpg
      ├── photo2.jpg
      └── photo3.jpg
    
    Proceso:
    - Encuentra todas las imágenes
    - Aplica el mismo pipeline a cada una
    - Muestra progreso
    - Guarda resultados
    
    Salida:
    output/batch/
      ├── photo1.jpg  (procesada)
      ├── photo2.jpg  (procesada)
      └── photo3.jpg  (procesada)
    """)
    
    print("\n💡 Ejemplo de código:")
    print("""
    from core import BatchProcessor, FilterPipeline
    from filters import BlurFilter, BrightnessFilter
    
    # Crear pipeline
    pipeline = FilterPipeline([
        BlurFilter(radius=3),
        BrightnessFilter(factor=1.3)
    ])
    
    # Crear procesador
    processor = BatchProcessor(
        input_dir='images/',
        output_dir='output/batch/',
        pipeline=pipeline
    )
    
    # Procesar todas las imágenes
    results = processor.process_all()
    
    # Ver resultados
    print(f"Procesadas: {results['successful']}/{results['total']}")
    print(f"Tiempo total: {results['total_time']:.2f}s")
    
    # Ver detalles de cada imagen
    for result in results['results']:
        if result['status'] == 'success':
            print(f"✓ {result['input_path']} → {result['output_path']}")
        else:
            print(f"✗ {result['input_path']}: {result['error']}")
    """)
    
    print("\n🎯 Casos de uso:")
    print("""
    ✓ Procesar fotos de eventos
    ✓ Normalizar imágenes para un dataset
    ✓ Aplicar watermarks o logos
    ✓ Redimensionar imágenes en lote
    ✓ Convertir formatos
    """)

