from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter
import multiprocessing
from functools import partial

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
        bottom = (i + 1) * part_height if i != num_parts - 1 else height
        part = image.crop((0, top, width, bottom))
        parts.append(part)
    return parts

def apply_filter_to_part(part, sigma=2.0):
    """
    Aplica un filtro de desenfoque (filtro gaussiano) a una parte de la imagen.
    
    Args:
    - part: Una parte de la imagen.
    - sigma: Parámetro del filtro gaussiano (desenfoque).
    
    Returns:
    - La parte de la imagen filtrada.
    """
    # Convertir la imagen a un array numpy
    np_array = np.array(part)
    
    # Aplicar el filtro gaussiano
    filtered_array = gaussian_filter(np_array, sigma=sigma)
    
    # Convertir el array de nuevo a una imagen
    filtered_image = Image.fromarray(np.uint8(filtered_array))
    
    # Convertir la imagen a modo 'RGB' si es necesario
    if filtered_image.mode != 'RGB':
        filtered_image = filtered_image.convert('RGB')
    
    return filtered_image

def process_image_parts(image_parts, sigma=2.0):
    """
    Procesa cada parte de la imagen en paralelo aplicando un filtro.
    
    Args:
    - image_parts: Lista de partes de la imagen.
    - sigma: Parámetro del filtro gaussiano (desenfoque).
    
    Returns:
    - Una lista de partes de la imagen filtradas.
    """
    with multiprocessing.Pool() as pool:
        # Usar `partial` para fijar el valor de sigma
        process_func = partial(apply_filter_to_part, sigma=sigma)
        # Aplicar el filtro a cada parte en paralelo
        filtered_parts = pool.map(process_func, image_parts)
    return filtered_parts

def main(image_path, num_parts, sigma=2.0):
    """
    Función principal para cargar, dividir, procesar y mostrar la imagen.
    
    Args:
    - image_path: Ruta a la imagen en el disco.
    - num_parts: Número de partes en las que se dividirá la imagen.
    - sigma: Parámetro del filtro gaussiano (desenfoque).
    """
    # Cargar la imagen
    image = load_image(image_path)
    
    # Dividir la imagen en partes
    image_parts = split_image(image, num_parts)
    
    # Procesar las partes en paralelo
    filtered_parts = process_image_parts(image_parts, sigma)
    
    # Mostrar cada parte filtrada
    for i, part in enumerate(filtered_parts):
        part.show()
    
    # Opcional: Guardar cada parte filtrada
    for i, part in enumerate(filtered_parts):
        part.save(f'parte_filtrada_{i}.jpg')

# Ejemplo de uso
if __name__ == "__main__":
    image_path = "/home/luciano/Descargas/um_logo.png"  # Ruta de la imagen en el disco
    num_parts = 2  # Número de partes en las que se dividirá la imagen
    sigma = 2.0  # Parámetro del filtro gaussiano
    main(image_path, num_parts, sigma)