import socket
import threading
from cthread import ClientThread

PORT = 7790
host = socket.gethostname()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, PORT))
print("Server started")
print("Waiting for client request..")

while True:
    server.listen(5)
    c_socket, c_address = server.accept()
    newthread = ClientThread(c_socket, c_address)
    newthread.start()