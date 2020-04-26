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
        self.argv = ""
        print("New connection.")

    def usage(self):
        action = self.argv[0]
        if "register" == action:
            return "Usage: register <username> <email> <password>"
        elif "login" == action:
            return "Usage: login <username> <password>"
        elif "list-board" == action:
            return "Usage: list-board ##<key>"
        elif "list-post" == action:
            return "Usage: list-post <board-name> ##<key>"
        elif "read" == action:
            return "Usage: read <post-id>"        
        
        elif not self.logged_in:
            return "Please login first."

        elif "create-board" == action:
            return "Usage: create-board <name>"
        elif "create-post" == action:
            return "Usage: create-post <board-name> --title <title> --content <content>"
        elif "delete-post" == action:
            return "Usage: delete-post <post-id>"
        elif "update-post" == action:
            return "Usage: update-post <post-id> --title/content <new>"
        elif "comment" == action:
            return "Usage: comment <post-id> <comment>"
        return ""

    def regisiter(self):
        username = self.argv[1]
        email = self.argv[2]
        password = self.argv[3]
        if db.insert_user(username, email, password) == 0:
            return "Register successfully."
        else:
            return "Username is already used."

    def login(self):
        if self.logged_in:
            return "Please logout first."
        else:
            username = self.argv[1]
            password = self.argv[2]
            if db.login_check(username, password):
                self.logged_in = True
                self.username = username
                return "Welcome, " + self.username + "."
            else:
                return "Login failed."

    def logout(self):
        username = self.username
        self.logged_in = False
        self.username = ""
        return "Bye, " + username

    def whoami(self):
        return self.username

    def create_board(self):
        boardname = self.argv[1]
        if db.insert_board(self.username, boardname) == 0:
            return "Create board successfully."
        else:
            return "Board already exist."

    def create_post(self):
        boardname = ""
        title = ""
        content = ""        
        argc = len(self.argv)        
        status = 0
        
        for arg in self.argv:
            if 0 == status:
                status = 1
            elif 1 == status:
                if arg == "--title":
                    status = 2
                else:
                    boardname = arg
            elif 2 == status:
                if arg == "--content":
                    status = 3
                else:
                    title = arg if title == "" else title + " " + arg
            elif 3 == status:
                content = arg if content == "" else content + " " + arg
        content = content.replace("<br>", "\r\n")

        if status != 3 or boardname == "":
            return self.usage()        
        elif db.insert_post(boardname, self.username, title, content) == 0:
            return "Create post successfully."
        else:
            return "Board does not exist."

    def list_board(self):
        header = "    Index   Name            Moderator"
        data = ""
        key = ""
        if len(self.argv) == 2:
            if self.argv[1][0:2] == "##":
                key = self.argv[1][2:]
            else:
                return self.usage()
        results = db.select_board(key)
        i = 1
        for row in results:
            data += "\r\n    {}{}{}".format(str(i).ljust(8, ' '), row[2].ljust(16, ' '), row[1])
            i += 1
        return header + data

    def list_post(self):
        boardname = self.argv[1]
        if not db.board_existed_check(boardname):
            return "Board does not exist."
        
        header = "    ID      Title           Author          Date"
        data = ""
        key = ""
        if len(self.argv) == 3:
            if self.argv[2][0:2] == "##":
                key = self.argv[2][2:]
            else:
                return self.usage()
        results = db.select_post(boardname = boardname, key = key)
        for row in results:
            data += "\r\n    {}{}{}{}".format(str(row[0]).ljust(8, ' '), row[1].ljust(16, ' '), row[2].ljust(16, ' '), row[3][5:7]+'/'+row[3][8:10])
        return header + data

    def read_post(self):
        pid = int(self.argv[1])
        if not db.post_existed_check(pid):
            return "Post does not exist."

        post = ""
        result = db.select_post(pid = pid)
        content = result[0][3].replace("\r\n", "\r\n    ")
        post = "    Author\t:{}\r\n    Title\t:{}\r\n    Date\t:{}\r\n    --\r\n    {}\r\n    --".format(result[0][0], result[0][1], result[0][2], content)      
        comments = ""
        results = db.select_comment(pid = pid)
        for row in results:
            comments += "\r\n    {}: {}".format(row[2], row[3])
        return post + comments

    def delete_post(self):
        pid = int(self.argv[1])
        action = db.delete_post(pid, self.username)
        if action == 0:
            return "Delete successfully."
        elif action == 2:
            return "Post does not exist."
        else:
            return "Not the post owner."

    def update_post(self):
        pid = int(self.argv[1])
        title_or_content = self.argv[2]
        argi = 3
        change = ""
        while argi < len(self.argv):
            change = self.argv[argi] if change == "" else change + " " + self.argv[argi]
            argi += 1
        if title_or_content != "--title" and title_or_content != "--content":
            return self.usage()
        elif title_or_content == "--content":
            change = change.replace("<br>", "\r\n")
        action = db.update_post(pid, self.username, title_or_content, change)
        if action == 0:
            return "Update successfully."
        elif action == 2:
            return "Post does not exist."
        else:
            return "Not the post owner."

    def comment(self):
        pid = int(self.argv[1])
        comment = ""
        argi = 2
        while argi < len(self.argv):
            comment = self.argv[argi] if comment == "" else comment + " " + self.argv[argi]
            argi += 1
        if db.insert_comment(pid, self.username, comment) == 0:
            return "Comment successfully."
        else:
            return "Post does not exist."
        
    def run(self):
        msg = "********************************\r\n" \
              "** Welcome to the BBS server. **\r\n" \
              "********************************\r\n% "
        self.c_socket.send(bytes(msg,'UTF-8'))
        
        while True:
            msg = ""
            data = self.c_socket.recv(2048)
            user_input = data.decode()
            # self.argv = re.split(" |\r\n", user_input)
            self.argv = user_input.split()
            argc = len(self.argv)
            action = self.argv[0] if argc > 0 else ""

            if "exit" == action:
                self.c_socket.close()
                return
            elif "register" == action:                    
                msg = self.regisiter() if argc == 4 else self.usage()
            elif "login" == action:                    
                msg = self.login() if argc == 3 else self.usage()
            elif "logout" == action:
                msg = self.logout() if self.logged_in else self.usage()
            elif "whoami" == action:
                msg = self.whoami() if self.logged_in else self.usage()            
            elif "create-board" == action:
                msg = self.create_board() if argc == 2 and self.logged_in else self.usage()
            elif "create-post" == action:
                msg = self.create_post() if argc >= 6 and self.logged_in else self.usage()
            elif "list-board" == action:
                msg = self.list_board() if argc <= 2 else self.usage()
            elif "list-post" == action:
                msg = self.list_post() if 2 <= argc <= 3 else self.usage()
            elif "read" == action:
                msg = self.read_post() if argc == 2 else self.usage()
            elif "delete-post" == action:
                msg = self.delete_post() if argc == 2 and self.logged_in else self.usage()
            elif "update-post" == action:
                msg = self.update_post() if argc >= 4 and self.logged_in else self.usage()
            elif "comment" == action:
                msg = self.comment() if argc >= 3 and self.logged_in else self.usage()

            msg = "% " if msg == "" else msg + "\r\n% "

            self.c_socket.send(bytes(msg,'UTF-8'))
