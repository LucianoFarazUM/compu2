# utils.py

import asyncio

async def send_to_scale_server(image_data, scale_factor):
    reader, writer = await asyncio.open_connection('localhost', 9999)
    
    # Convertir el factor de escala a bytes
    scale_data = f"{scale_factor}".encode()
    
    # Preparar un encabezado de 4 bytes para la longitud de la imagen
    image_length = len(image_data).to_bytes(4, byteorder='big')
    
    # Enviar longitud de la imagen, datos de la imagen y luego el factor de escala
    writer.write(image_length + image_data + scale_data)
    await writer.drain()

    # Recibir la imagen escalada del servidor de escalado
    data = await reader.read(1024 * 1024)
    writer.close()
    await writer.wait_closed()
    return data