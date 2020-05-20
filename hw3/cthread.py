import time
import random, string
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
        self.username = ''
        self.argv = ''
        self.bucket = ''
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
        elif 'mail-to' == action:
            return 'Usage: mail-to <username> --subject <subject> --content <content>'
        elif 'retr-mail' == action:
            return 'Usage: retr-mail <mail#>'
        elif 'delete-mail' == action:
            return 'Usage: delete-mail <mail#>'
        return ""

    def regisiter(self):
        username = self.argv[1]
        email = self.argv[2]
        password = self.argv[3]
        bucket = 'nphw0616026user' + str(int(time.time()*100000)) + ''.join(random.choice(string.ascii_lowercase) for i in range(8))
        if db.insert_user(username, email, password, bucket) == 0:
            return '&<!register::>' + bucket + "&<!meta|msg>Register successfully."
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
                self.bucket = db.get_bucket(username)
                return "Welcome, " + self.username + "." + self.bucket
            else:
                return "Login failed."

    def logout(self):
        username = self.username
        self.logged_in = False
        self.username = ""
        self.bucket = ''
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
        object_name = 'post' + str(int(time.time())) + ''.join(random.choice(string.ascii_lowercase) for i in range(8)) + '.txt'
        comment_object_name = 'comment' + str(int(time.time())) + ''.join(random.choice(string.ascii_lowercase) for i in range(8)) + '.txt'

        if status != 3 or boardname == "":
            return self.usage()        
        elif db.insert_post(boardname, self.username, title, object_name, comment_object_name) == 0:
            return '&<!create-post>' + self.bucket + '&<!spl>' + object_name + '&<!spl>' + content + '&<!spl>' + comment_object_name + "&<!meta|msg>Create post successfully."
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
        # content = result[0][3].replace("\r\n", "\r\n    ")
        object_name = result[0][3]
        comment_object_name = result[0][4]
        post = "Author\t:{}\r\nTitle\t:{}\r\nDate\t:{}\r\n--\r\n".format(result[0][0], result[0][1], result[0][2])      
        # comments = ""
        # results = db.select_comment(pid = pid)
        # for row in results:
        #     comments += "\r\n    {}: {}".format(row[2], row[3])
        return '&<!read::>' + db.get_bucket(result[0][0]) + '&<!spl>' + object_name + '&<!spl>' + comment_object_name + '&<!meta|msg>' + post

    def delete_post(self):
        pid = int(self.argv[1])
        object_name = db.get_post_object_name(pid)
        comment_object_name = db.get_comment_object_name(pid)
        action = db.delete_post(pid, self.username)
        if action == 0:
            return '&<!delete-post::>' + db.get_bucket(self.username) + '&<!spl>' + object_name + '&<!spl>' + comment_object_name + '&<!meta|msg>' + "Delete successfully."
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
        elif action == 5:
            bucket = db.get_bucket(self.username)
            object_name = db.get_post_object_name(pid)
            return '&<!update-post-content>' + bucket + '&<!spl>' + object_name + '&<!spl>' + change + '&<!meta|msg>Update successfully.'
        else:
            return "Not the post owner."

    def comment(self):
        pid = int(self.argv[1])
        if not db.post_existed_check(pid):
            return "Post does not exist."

        comment = self.username + ":"
        argi = 2
        while argi < len(self.argv):
            comment = self.argv[argi] if comment == "" else comment + " " + self.argv[argi]
            argi += 1
        result = db.insert_comment(pid)
        bucket = db.get_bucket(result[0])
        comment_object_name = result[1]
        return '&<!comment>' + bucket + '&<!spl>' + comment_object_name + '&<!spl>' + comment + '&<!meta|msg>Comment successfully.'
        
    def mail_to(self):
        receiver = ""
        subject = ""
        content = ""        
        argc = len(self.argv)        
        status = 0
        
        for arg in self.argv:
            if 0 == status:
                status = 1
            elif 1 == status:
                if arg == "--subject":
                    status = 2
                else:
                    receiver = arg
            elif 2 == status:
                if arg == "--content":
                    status = 3
                else:
                    subject = arg if subject == "" else subject + " " + arg
            elif 3 == status:
                content = arg if content == "" else content + " " + arg
        content = content.replace("<br>", "\r\n")
        object_name = 'mail' + str(int(time.time())) + ''.join(random.choice(string.ascii_lowercase) for i in range(8)) + '.txt'

        if status != 3 or receiver == "":
            return self.usage()        
        elif db.insert_mail(self.username, receiver, subject, object_name) == 0:
            bucket = db.get_bucket(receiver)
            return '&<!mail-to>' + bucket + '&<!spl>' + object_name + '&<!spl>' + content + "&<!meta|msg>Sent successfully."
        else:
            return receiver + " does not exist."

    def list_mail(self):
        username = self.username
        
        header = "ID      Subject         From            Date"
        data = ""
        
        results = db.select_mail(receiver = username)

        idx = 1
        for row in results:
            data += "\r\n{}{}{}{}".format(str(idx).ljust(8, ' '), row[0].ljust(16, ' '), row[1].ljust(16, ' '), row[2][5:7]+'/'+row[2][8:10])
            idx += 1
        return header + data

    def retr_mail(self):
        index = int(self.argv[1])
        username = self.username
        mail = ''
        results = db.select_mail(receiver = username)

        if 0 < index <= len(results):
            mail = 'Subject\t:{}\r\nFrom\t:{}\r\nDate\t:{}\r\n--\r\n'.format(results[index-1][0], results[index-1][1], results[index-1][2])
        else:
            return 'No such mail.'

        object_name = results[index-1][3]

        return '&<!retr-mail::>' + db.get_bucket(username) + '&<!spl>' + object_name + '&<!meta|msg>' + mail

    def delete_mail(self):
        index = int(self.argv[1])
        username = self.username
        mail = ''
        results = db.select_mail(receiver = username)

        if 0 < index <= len(results):
            db.delete_mail(results[index-1][4])
            return '&<!delete-mail::>' + db.get_bucket(username) + '&<!spl>' + results[index-1][3] + '&<!meta|msg>Mail deleted.'
        else:
            return 'No such mail.'


    def run(self):
        msg = "********************************\r\n" \
              "** Welcome to the BBS server. **\r\n" \
              "********************************"
        self.c_socket.send(bytes(msg,'UTF-8'))
        
        while True:
            msg = " "
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
            elif 'mail-to' == action:
                msg = self.mail_to() if argc >= 6 and self.logged_in else self.usage()
            elif 'list-mail' == action:
                msg = self.list_mail() if argc <= 2 and self.logged_in else self.usage()
            elif 'retr-mail' == action:
                msg = self.retr_mail() if argc == 2 and self.logged_in else self.usage()
            elif 'delete-mail' == action:
                msg = self.delete_mail() if argc == 2 and self.logged_in else self.usage()

            # msg = "% " if msg == "" else msg + "\r\n% "

            self.c_socket.send(bytes(msg,'UTF-8'))
