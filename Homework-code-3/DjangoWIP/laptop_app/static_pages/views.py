from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(_):
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>💻 Catálogo de Laptops - Home</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #e6f2ff; }
            .container { max-width: 800px; margin: 0 auto; background: white; 
                        padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            nav a { margin-right: 15px; text-decoration: none; color: #0066cc; font-weight: bold; }
            h1 { color: #003d7a; }
            .product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }
            .product { border: 1px solid #ddd; padding: 15px; border-radius: 5px; background: #f9f9f9; }
            .price { color: #28a745; font-weight: bold; font-size: 1.1em; }
        </style>
    </head>
    <body>
        <div class="container">
            <nav>
                <a href="/static-pages/">🏠 Home</a>
                <a href="/static-pages/about/">ℹ️ About</a>
                <a href="/static-pages/contact/">📧 Contact</a>
                <a href="/dynamic-pages/">🎨 Catálogo Dinámico</a>
                <a href="/api/laptops/">🔌 API</a>
            </nav>
            
            <h1>💻 Bienvenido a Laptop Catalog</h1>
            <p><strong>¿Qué es contenido estático?</strong></p>
            <ul>
                <li>✅ HTML completamente fijo</li>
                <li>✅ No consulta base de datos</li>
                <li>✅ Respuesta muy rápida</li>
                <li>✅ Ideal para landing pages</li>
            </ul>
            
            <h3>💻 Laptops Destacadas (Estáticas)</h3>
            <div class="product-grid">
                <div class="product">
                    <h4>Asus</h4>
                    <p>RAM: 4 GB | SSD: 256 GB</p>
                    <p>Sistema: Windows 10</p>
                    <p class="price">$ 1.577.000</p>
                </div>
                <div class="product">
                    <h4>Lenovo</h4>
                    <p>RAM: 8 GB | SSD: 256 GB</p>
                    <p>Sistema: Windows 11</p>
                    <p class="price">$ 1.400.000</p>
                </div>
            </div>
            
            <p><em>Esta página está definida directamente en el código Python.</em></p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)


def about(_):
    """Página About estática"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>📋 Acerca de</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #e6f2ff; }
            .container { max-width: 600px; margin: 0 auto; background: white; 
                        padding: 30px; border-radius: 10px; }
            h1 { color: #003d7a; }
            a { color: #0066cc; text-decoration: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📋 Acerca del Catálogo de Laptops</h1>
            <p>Esta es una página estática creada con Django.</p>
            <p><strong>Características:</strong></p>
            <ul>
                <li>No usa base de datos</li>
                <li>HTML fijo definido en views.py</li>
                <li>Respuesta inmediata</li>
                <li>Catálogo de laptops con especificaciones técnicas</li>
            </ul>
            <a href="/static-pages/">← Volver al Home</a>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)