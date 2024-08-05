import signal
import time
import multiprocessing
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter

interrupted = False

def signal_handler(sig, frame):
    """
    Maneja la señal de interrupción (SIGINT) para permitir una interrupción controlada.
    """
    global interrupted
    print('Interrupción recibida. Finalizando...')
    interrupted = True

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
    try:
        filtered_part = apply_filter_to_part(part, sigma)
        pipe_send.send(filtered_part)
    except Exception as e:
        print(f"Error en proceso trabajador: {e}")
    finally:
        pipe_send.close()

def process_image_parts_parallel(image_parts, sigma=2.0):
    """
    Procesa cada parte de la imagen en paralelo aplicando un filtro y usa Pipes para la comunicación.
    """
    pipes = [multiprocessing.Pipe() for _ in range(len(image_parts))]
    processes = []
    
    for i, (part, (pipe_recv, pipe_send)) in enumerate(zip(image_parts, pipes)):
        if interrupted:
            break
        p = multiprocessing.Process(target=worker_function, args=(part, sigma, pipe_send))
        processes.append(p)
        p.start()
    
    filtered_parts = []
    for pipe_recv, _ in pipes:
        if interrupted:
            break
        try:
            filtered_part = pipe_recv.recv()
            filtered_parts.append(filtered_part)
        except EOFError:
            print("Error en la recepción de datos.")
        finally:
            pipe_recv.close()
    
    for p in processes:
        p.join()
    
    return filtered_parts

def process_image_parts_sequential(image_parts, sigma=2.0):
    """
    Procesa cada parte de la imagen de manera secuencial aplicando un filtro.
    """
    filtered_parts = []
    for part in image_parts:
        if interrupted:
            break
        filtered_part = apply_filter_to_part(part, sigma)
        filtered_parts.append(filtered_part)
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

def main(image_path, num_parts, sigma=2.0):
    """
    Función principal para medir el rendimiento del procesamiento secuencial y paralelo.
    """
    global interrupted

    # Cargar la imagen
    image = load_image(image_path)
    image_parts = split_image(image, num_parts)

    # Procesamiento Secuencial
    interrupted = False 
    start_time = time.time()
    filtered_parts_sequential = process_image_parts_sequential(image_parts, sigma)
    combined_image_sequential = combine_image_parts(filtered_parts_sequential)
    end_time = time.time()
    sec_time = end_time - start_time
    print(f"Tiempo de procesamiento secuencial: {sec_time:.2f} segundos")

    # Guardar la imagen secuencial para comparación
    combined_image_sequential.save('imagen_secuencial.jpg')

    # Procesamiento Paralelo
    interrupted = False  
    start_time = time.time()
    filtered_parts_parallel = process_image_parts_parallel(image_parts, sigma)
    combined_image_parallel = combine_image_parts(filtered_parts_parallel)
    end_time = time.time()
    par_time = end_time - start_time
    print(f"Tiempo de procesamiento paralelo: {par_time:.2f} segundos")

    # Guardar la imagen paralela para comparación
    combined_image_parallel.save('imagen_paralela.jpg')

# Configurar el manejador de señales
signal.signal(signal.SIGINT, signal_handler)


if __name__ == "__main__":
    image_path = "/home/luciano/Descargas/um_logo.png" 
    num_parts = 2  # Número de partes en las que se dividirá la imagen
    sigma = 2.0  # Parámetro del filtro gaussiano
    main(image_path, num_parts, sigma)