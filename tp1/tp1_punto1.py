from PIL import Image

def cargar_y_dividir_imagen(ruta_imagen, n_partes):
    imagen = Image.open(ruta_imagen)
    ancho, alto = imagen.size
    altura_parte = alto // n_partes
    partes = []

    for i in range(n_partes):
        top = i * altura_parte
        bottom = (i + 1) * altura_parte if i < n_partes - 1 else alto
        parte = imagen.crop((0, top, ancho, bottom))
        partes.append(parte)

    return partes

def guardar_partes(partes, ruta_salida_base):
  
    for i, parte in enumerate(partes):
        ruta_salida = f'{ruta_salida_base}_parte_{i + 1}.png'
        parte.save(ruta_salida)
        print(f'Parte {i + 1} guardada en: {ruta_salida}')

if __name__ == "__main__":
    try:
        ruta_imagen = "/home/luciano/Escritorio/compu2/TPS/tp1/um_logo.png"
        
        n_partes = int(input('Ingrese el número de partes que quiera: '))
        partes = cargar_y_dividir_imagen(ruta_imagen, n_partes)
        
        ruta_salida_base = 'parte_imagen'
        guardar_partes(partes, ruta_salida_base)
    except Exception as e:
        print(f"Ocurrió un error: {e}")