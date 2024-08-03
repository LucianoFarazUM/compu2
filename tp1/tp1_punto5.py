from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter
import multiprocessing
from multiprocessing import Array
import ctypes

def load_image(image_path):
    """
    Carga una imagen desde el disco utilizando PIL (Pillow).
    """
    return Image.open(image_path).convert('RGB')  # Asegúrate de que la imagen esté en formato RGB

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

def apply_filter_to_array(np_array, sigma=2.0):
    """
    Aplica un filtro de desenfoque (filtro gaussiano) a una parte de la imagen en formato numpy array.
    """
    filtered_array = gaussian_filter(np_array, sigma=sigma)
    return np.uint8(filtered_array)

def worker_function(start_row, end_row, shared_array, width, height, sigma):
    """
    Función del trabajador que procesa una parte de la imagen y almacena el resultado en un array compartido.
    """
    # Convertir el array compartido a un numpy array
    np_array_shared = np.frombuffer(shared_array.get_obj(), dtype=np.uint8).reshape((height, width, 3))
    
    # Procesar la parte correspondiente de la imagen
    for row in range(start_row, end_row):
        np_array_shared[row, :, :] = apply_filter_to_array(np_array_shared[row, :, :], sigma)

def process_image_parts_with_shared_memory(image_parts, num_parts, sigma=2.0):
    """
    Procesa cada parte de la imagen en paralelo utilizando memoria compartida.
    """
    width, height = image_parts[0].size
    # Crear un array compartido para almacenar los resultados
    shared_array = Array(ctypes.c_uint8, width * height * 3)
    
    # Convertir las partes de la imagen a un array numpy y copiar al array compartido
    np_array_shared = np.frombuffer(shared_array.get_obj(), dtype=np.uint8).reshape((height, width, 3))
    for i, part in enumerate(image_parts):
        part_np = np.array(part.convert('RGB'))  # Convertir a RGB
        start_row = i * (height // num_parts)
        end_row = (i + 1) * (height // num_parts) if i != num_parts - 1 else height
        np_array_shared[start_row:end_row, :, :] = part_np[:end_row - start_row, :, :]  # Asegúrate de que las dimensiones coincidan
    
    processes = []
    rows_per_process = height // num_parts
    for i in range(num_parts):
        start_row = i * rows_per_process
        end_row = (i + 1) * rows_per_process if i != num_parts - 1 else height
        p = multiprocessing.Process(target=worker_function, args=(start_row, end_row, shared_array, width, height, sigma))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    # Crear una imagen final combinando los resultados procesados
    combined_image = Image.fromarray(np_array_shared)
    return combined_image

def main(image_path, num_parts, sigma=2.0):
    """
    Función principal para cargar, dividir, procesar y mostrar la imagen.
    """
    image = load_image(image_path)
    image_parts = split_image(image, num_parts)
    combined_image = process_image_parts_with_shared_memory(image_parts, num_parts, sigma)
    combined_image.show()
    combined_image.save('imagen_combinada_con_memoria_compartida.jpg')

# Ejemplo de uso
if __name__ == "__main__":
    image_path = "/home/luciano/Descargas/um_logo.png"  # Ruta de la imagen en el disco
    num_parts = 2  # Número de partes en las que se dividirá la imagen
    sigma = 2.0  # Parámetro del filtro gaussiano
    main(image_path, num_parts, sigma)