import socket
import threading

class ClientThread(threading.Thread):
    def __init__(self, c_socket_, c_address_):
        threading.Thread.__init__(self)
        self.c_socket = c_socket_
        self.c_address = c_address_
        print ("New connection added: ", self.c_address)
    
    def run(self):
        print ("Connection from : ", self.c_address)
        #self.c_socket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        while True:
            data = self.c_socket.recv(2048)
            msg = data.decode()
            # text = msg.split(" ")
            # if msg == "bye\r\n":
            #     break
            if "bye" in msg:
                self.c_socket.close()
                break
            print ("from client", msg)
            self.c_socket.send(bytes(msg,'UTF-8'))
        print ("Client at ", self.c_address , " disconnected...")