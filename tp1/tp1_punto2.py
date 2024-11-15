from scipy.ndimage import gaussian_filter
from PIL import Image
import numpy as np
import multiprocessing

def procesar_imagen_desde_ruta(ruta_imagen, ruta_salida='imagen_filtrada.jpg', num_procesos=4, sigma=1):
    
    # Cargar la imagen
    imagen = Image.open(ruta_imagen).convert('L')  # Convertir a escala de grises
    array_imagen = np.array(imagen)

    # Aplicar el filtro en paralelo
    imagen_filtrada = procesar_imagen_en_paralelo(array_imagen, num_procesos=num_procesos, sigma=sigma)

    # Convertir el array filtrado de nuevo a una imagen y guardarla
    imagen_filtrada_pil = Image.fromarray(imagen_filtrada)
    imagen_filtrada_pil.save(ruta_salida)

def aplicar_filtro(parte_imagen, sigma=1):
  
    return gaussian_filter(parte_imagen, sigma=sigma)

def dividir_imagen(imagen, num_partes):
    altura, ancho = imagen.shape
    altura_parte = altura // num_partes
    partes = [imagen[i * altura_parte:(i + 1) * altura_parte] for i in range(num_partes)]
    return partes

def procesar_imagen_en_paralelo(imagen, num_procesos=4, sigma=1):
    # Dividir la imagen en partes
    partes_imagen = dividir_imagen(imagen, num_procesos)

    
    with multiprocessing.Pool(processes=num_procesos) as pool:
        
        partes_filtradas = pool.starmap(aplicar_filtro, [(parte, sigma) for parte in partes_imagen])

    # Combinar las partes filtradas
    imagen_filtrada = np.vstack(partes_filtradas)

    return imagen_filtrada

if __name__ == "__main__":
    ruta_imagen = "/home/luciano/Escritorio/compu2/TPS/tp1/um_logo.png"
    num_procesos = 4
    sigma = 1
    ruta_salida = 'imagen_filtrada.jpg'

    procesar_imagen_desde_ruta(ruta_imagen, ruta_salida, num_procesos, sigma)