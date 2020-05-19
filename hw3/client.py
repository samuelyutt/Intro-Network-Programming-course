import sys, socket


PORT = 7788  # socket server port number

if len(sys.argv) == 2:
    PORT = int(sys.argv[1])

host = socket.gethostname()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, PORT))

# while message.lower().strip() != 'bye':
while True:

    msg = client.recv(1024).decode()
    print(msg, end='')

    data = input()
    client.send(data.encode())

    if data == 'exit':
        break

client.close()