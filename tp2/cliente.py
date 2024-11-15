import socket
import os

def send_image(image_path, server_ip, server_port):
    try:
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # Preparar conexión y enviar tamaño de la imagen como encabezado (4 bytes)
        data_size = len(image_data)
        with socket.create_connection((server_ip, server_port)) as sock:
            sock.sendall(data_size.to_bytes(4, byteorder='big'))
            sock.sendall(image_data)  # Enviar datos de la imagen
            
            # Recibir la imagen procesada
            result = sock.recv(1024 * 1024)
            with open("output.png", "wb") as f_out:
                f_out.write(result)
            print("Imagen procesada recibida y guardada como 'output.png'.")
    except FileNotFoundError:
        print(f"No se encontró la imagen en la ruta especificada: {image_path}")

if __name__ == "__main__":
    # Solicitar la ruta de la imagen al usuario
    image_path = input("Por favor ingresa la ruta de la imagen que deseas procesar: ")
    send_image(image_path, "127.0.0.1", 8888)