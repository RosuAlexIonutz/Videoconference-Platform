import socket
import threading

class VideoServer:
    def __init__(self, host, port):
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024 * 1024)
                if not data:
                    break
                for client in self.clients:
                    if client != client_socket:
                        client.send(data)
            except Exception as e:
                print(f"Error handling data from client: {e}")
                break
        client_socket.close()
        self.clients.remove(client_socket)

    def start(self):
        print("Server started, waiting for connections...")
        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Connected with {addr}")
            self.clients.append(client_socket)
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    server = VideoServer('0.0.0.0', 5000)
    server.start()
