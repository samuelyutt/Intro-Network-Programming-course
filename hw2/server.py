import sys
import socket
import threading
import db
from cthread import ClientThread

PORT = 7788

db.create_all_tables()

if len(sys.argv) == 2:
    PORT = int(sys.argv[1])

host = socket.gethostname()
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((host, PORT))
print("Server started on", host, "using port", PORT)

while True:
    server.listen(5)
    c_socket, c_address = server.accept()
    new_connection = ClientThread(c_socket, c_address)
    new_connection.start()