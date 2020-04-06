import socket
import threading
import re
import db

class ClientThread(threading.Thread):
    def __init__(self, c_socket_, c_address_):
        threading.Thread.__init__(self)
        self.c_socket = c_socket_
        self.c_address = c_address_
        self.logged_in = False
        self.username = ""
        # print ("New connection added: ", self.c_address)

    def regisiter(self, username, email, password):
        action = db.insert_user(username, email, password)
        if action == 0:
            return "Register successfully."
        else:
            return "Username is already used."

    def login(self, username, password):
        if self.logged_in:
            return "Please logout first."
        else:
            if db.login_check(username, password):
                self.logged_in = True
                self.username = username
                return "Welcome, " + self.username + "."
            else:
                return "Login failed."

    def logout(self):
        if self.logged_in:
            username = self.username
            self.logged_in = False
            self.username = ""
            return "Bye, " + username
        else:
            return "Please login first."

    def whoami(self):
        if self.logged_in:
            return self.username
        else:
            return "Please login first."
    
    def run(self):
        # print ("Connection from : ", self.c_address)
        msg = "% "
        self.c_socket.send(bytes(msg,'UTF-8'))
        while True:
            msg = ""
            data = self.c_socket.recv(2048)
            imput = data.decode()
            argv = re.split(" |\r\n", imput)

            if argv[0] == "register":
                if len(argv) == 5:
                    msg = self.regisiter(argv[1], argv[2], argv[3])
                else:
                    msg = "Usage: register <username> <email> <password>"
            elif argv[0] == "login":
                if len(argv) == 4:
                    msg = self.login(argv[1], argv[2])
                else:
                    msg = "Usage: login <username> <password>"
            elif argv[0] == "logout":
                msg = self.logout()
            elif argv[0] == "whoami":
                msg = self.whoami()
            elif argv[0] == "exit":
                self.c_socket.close()
                return
            
            
            # if "bye" in msg:
            #     self.c_socket.close()
            #     break
            # print ("from client", msg)
            msg += "\r\n% "
            self.c_socket.send(bytes(msg,'UTF-8'))
        


        # print ("Client at ", self.c_address , " disconnected...")