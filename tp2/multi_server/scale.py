# scale_server.py

from multiprocessing import Process
from socketserver import BaseRequestHandler, TCPServer
from PIL import Image
import io

class ScaleHandler(BaseRequestHandler):
    def handle(self):
        try:
            # Leer los primeros 4 bytes que representan la longitud de la imagen
            image_length_bytes = self.request.recv(4)
            if not image_length_bytes:
                print("Error: No se recibió la longitud de la imagen.")
                return

            image_length = int.from_bytes(image_length_bytes, byteorder='big')
            print(f"Tamaño de la imagen recibido: {image_length} bytes")
            
            # Leer los datos de la imagen completos en fragmentos
            image_data = b""
            while len(image_data) < image_length:
                packet = self.request.recv(image_length - len(image_data))
                if not packet:
                    print("Error: Conexión cerrada antes de recibir todos los datos de la imagen.")
                    return
                image_data += packet
            
            # Leer el resto de los datos como factor de escala
            scale_factor_data = self.request.recv(1024)  # Tamaño máximo esperado para el factor de escala
            scale_factor = float(scale_factor_data.decode())
            print(f"Factor de escala recibido: {scale_factor}")
            
            # Escalar la imagen
            image = Image.open(io.BytesIO(image_data))
            new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
            image = image.resize(new_size)
            
            # Enviar la imagen escalada al primer servidor
            output = io.BytesIO()
            image.save(output, format="PNG")
            self.request.sendall(output.getvalue())
            print("Imagen escalada y enviada al primer servidor.")
        
        except Exception as e:
            print(f"Error en ScaleHandler: {e}")

def run_scale_server(host, port):
    with TCPServer((host, port), ScaleHandler) as server:
        print(f"Servidor de escalado escuchando en {host}:{port}")
        server.serve_forever()

if __name__ == "__main__":
    p = Process(target=run_scale_server, args=("localhost", 9999))
    p.start()