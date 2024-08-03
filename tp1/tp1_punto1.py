from PIL import Image
import numpy as np

def load_image(image_path):
    """
    Carga una imagen desde el disco utilizando PIL (Pillow).
    
    Args:
    - image_path: La ruta de la imagen en el disco.
    
    Returns:
    - La imagen cargada.
    """
    return Image.open(image_path)

def split_image(image, num_parts):
    """
    Divide una imagen en partes iguales.
    
    Args:
    - image: La imagen a dividir.
    - num_parts: El número de partes en las que se dividirá la imagen.
    
    Returns:
    - Una lista de imágenes, cada una representando una parte de la imagen original.
    """
    width, height = image.size
    part_height = height // num_parts
    parts = []
    for i in range(num_parts):
        top = i * part_height
        bottom = (i + 1) * part_height
        part = image.crop((0, top, width, bottom))
        parts.append(part)
    return parts

# Ejemplo de uso
image_path = "/home/luciano/Descargas/um_logo.png"  # Ruta de la imagen en el disco
num_parts = 2 # Número de partes en las que se dividirá la imagen

# Cargar la imagen
image = load_image(image_path)

# Dividir la imagen en partes
image_parts = split_image(image, num_parts)

# Mostrar cada parte de la imagen
for i, part in enumerate(image_parts):
    part.show()

# Ahora puedes procesar cada parte de la imagen en paralelo
