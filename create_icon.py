#!/usr/bin/env python3
"""
Script para crear un icono simple para la aplicación de control de brillo
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

def create_icon():
    """Crea un icono simple para la aplicación"""
    
    if not PIL_AVAILABLE:
        print("PIL/Pillow no está disponible. Intenta instalarlo:")
        print("pip install Pillow")
        return False
    
    # Crear imagen de 64x64 píxeles
    size = 64
    img = Image.new('RGBA', (size, size), (90, 90, 90, 255))  # Color #5a5a5a
    draw = ImageDraw.Draw(img)
    
    # Intentar usar una fuente, si no disponible usar fuente por defecto
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    # Dibujar texto "BRILLO" en el centro
    text = "BRILLO"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
    
    # Guardar icono
    img.save('icon.png', 'PNG')
    print("Icono creado exitosamente: icon.png")
    return True

if __name__ == "__main__":
    create_icon()
