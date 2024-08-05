import sys
import os
import numpy as np
import multiprocessing
from PIL import Image
from scipy.ndimage import gaussian_filter

# Agregar el directorio raíz al path (esto puede ser opcional dependiendo de tu estructura de directorios)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_image(image_path):
    """
    Carga una imagen desde el disco utilizando PIL (Pillow).
    """
    return Image.open(image_path)

def split_image(image, num_parts):
    """
    Divide una imagen en partes iguales.
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
    """
    np_array = np.array(part)
    filtered_array = gaussian_filter(np_array, sigma=sigma)
    filtered_image = Image.fromarray(np.uint8(filtered_array))
    if filtered_image.mode != 'RGB':
        filtered_image = filtered_image.convert('RGB')
    return filtered_image

def worker_function(part, sigma, pipe_send):
    """
    Función del trabajador que procesa una parte de la imagen y envía el resultado a través del pipe.
    """
    filtered_part = apply_filter_to_part(part, sigma)
    pipe_send.send(filtered_part)
    pipe_send.close()

def process_image_parts(image_parts, sigma=2.0):
    """
    Procesa cada parte de la imagen en paralelo aplicando un filtro y usa Pipes para la comunicación.
    """
    pipes = [multiprocessing.Pipe() for _ in range(len(image_parts))]
    processes = []
    
    for i, (part, (pipe_recv, pipe_send)) in enumerate(zip(image_parts, pipes)):
        p = multiprocessing.Process(target=worker_function, args=(part, sigma, pipe_send))
        processes.append(p)
        p.start()
    
    filtered_parts = []
    for pipe_recv, _ in pipes:
        filtered_part = pipe_recv.recv()
        filtered_parts.append(filtered_part)
        pipe_recv.close()
    
    for p in processes:
        p.join()
    
    return filtered_parts

def combine_image_parts(filtered_parts):
    """
    Combina las partes filtradas en una sola imagen.
    """
    widths, heights = zip(*(i.size for i in filtered_parts))
    total_height = sum(heights)
    
    combined_image = Image.new('RGB', (widths[0], total_height))
    y_offset = 0
    for part in filtered_parts:
        combined_image.paste(part, (0, y_offset))
        y_offset += part.height
    
    return combined_image

def procesar_imagen_con_comunicacion(ruta_imagen, ruta_salida='imagen_filtrada.jpg', num_procesos=4, sigma=2.0):
    """
    :param ruta_imagen: Ruta de la imagen a procesar.
    :param ruta_salida: Ruta donde se guardará la imagen filtrada.
    :param num_procesos: Número de procesos a usar para el filtrado.
    :param sigma: Desviación estándar para el filtro gaussiano.
    """
    imagen = load_image(ruta_imagen)
    
    partes_imagen = split_image(imagen, num_procesos)

    partes_filtradas = process_image_parts(partes_imagen, sigma)

    imagen_combinada = combine_image_parts(partes_filtradas)
    
    imagen_combinada.save(ruta_salida)

if __name__ == "__main__":
    ruta_imagen = "/home/luciano/Descargas/um_logo.png"
    num_procesos = 2
    sigma = 2.0
    ruta_salida = 'imagen_filtrada.jpg'
    procesar_imagen_con_comunicacion(ruta_imagen, ruta_salida, num_procesos, sigma)