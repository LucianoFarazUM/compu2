import asyncio
import argparse
from PIL import Image
import io
from tp2.server_asinc.utililades import send_to_scale_server  # Importa la función auxiliar para la comunicación con el segundo servidor

async def handle_client(reader, writer):
    try:
        # Leer el encabezado de 4 bytes que indica el tamaño de la imagen
        data_size_bytes = await reader.read(4)
        if not data_size_bytes:
            print("Error: No se recibió el tamaño de los datos.")
            writer.close()
            await writer.wait_closed()
            return

        data_size = int.from_bytes(data_size_bytes, byteorder='big')
        print(f"Tamaño de la imagen recibido: {data_size} bytes")

        # Leer los datos de la imagen en fragmentos hasta completar data_size
        data = b""
        while len(data) < data_size:
            packet = await reader.read(data_size - len(data))
            if not packet:
                print("Error: Conexión cerrada antes de recibir todos los datos de la imagen.")
                writer.close()
                await writer.wait_closed()
                return
            data += packet

        # Convertir a escala de grises
        try:
            image = Image.open(io.BytesIO(data)).convert("L")  # Convertir a escala de grises
            print("Imagen convertida a escala de grises.")
        except OSError as e:
            print(f"Error al abrir la imagen: {e}")
            writer.close()
            await writer.wait_closed()
            return

        # Convertir la imagen procesada a bytes
        output = io.BytesIO()
        image.save(output, format="PNG")

        # Enviar al servidor de escalado
        scaled_data = await send_to_scale_server(output.getvalue(), 0.7)  # Factor de escala 0.7 (ejemplo)
        print("Imagen escalada enviada de vuelta al cliente.")
        
        writer.write(scaled_data)
        await writer.drain()
    except Exception as e:
        print(f"Error en handle_client: {e}")
    finally:
        writer.close()
        await writer.wait_closed()


async def main(host, port):
    server = await asyncio.start_server(handle_client, host, port)
    print(f"Servidor escuchando en {host}:{port}")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de procesamiento de imágenes.")
    parser.add_argument("-i", "--ip", type=str, required=True, help="Dirección IP de escucha")
    parser.add_argument("-p", "--port", type=int, required=True, help="Puerto de escucha")
    args = parser.parse_args()

    asyncio.run(main(args.ip, args.port))