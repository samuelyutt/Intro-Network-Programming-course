import time
import random, string
import sqlite3


def login_check(username, password):
    # Return True if password matches username
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (username, password, )
    cursor = c.execute("SELECT COUNT(*) FROM USERS u WHERE u.username == ? AND u.password == ?", params)
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    return int(values[0]) > 0

def get_bucket(username):
    # Return True if password matches username
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (username,)
    cursor = c.execute("SELECT bucket FROM USERS u WHERE u.username == ?", params)
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    return values[0]

def get_comment_object_name(pid):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (pid,)
    cursor = c.execute("SELECT cmt_object FROM POSTS p WHERE p.pid == ?", params)
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    return values[0]

def get_post_object_name(pid):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (pid,)
    cursor = c.execute("SELECT object FROM POSTS p WHERE p.pid == ?", params)
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    return values[0]

def modify_post_check(pid, username):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (pid, )
    cursor = c.execute("SELECT author FROM POSTS p WHERE p.pid == ?", params)
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    if values == None:
        return 2
    elif values[0] != username:
        return 3
    else:
        return 0

def update_post(pid, username, title_or_content, change):
    check_err = modify_post_check(pid, username)
    if not check_err:
        if title_or_content == "--title":
            conn = sqlite3.connect('bbs.db')
            c = conn.cursor()
            params = (change, pid, username, )
            cursor = c.execute("UPDATE POSTS SET title = ? WHERE pid == ? AND author == ?", params)
            conn.commit()
            conn.close()
        elif title_or_content == "--content":
            check_err = 5
        else:
            check_err = 4
    return check_err

def delete_post(pid, username):
    check_err = modify_post_check(pid, username)
    if not check_err:
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        params = (pid, username, )
        cursor = c.execute("DELETE FROM POSTS WHERE pid == ? AND author == ?", params)
        conn.commit()
        conn.close()
    return check_err

def create_table_users():
    try:    
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE USERS(
                uid         INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL UNIQUE,
                email       TEXT    NOT NULL,
                password    TEXT    NOT NULL,
                bucket      TEXT    NOT NULL
            );
        ''')
        conn.commit()
        conn.close()
    except:
        pass

def create_table_boards():
    try:    
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE BOARDS(
                bid         INTEGER PRIMARY KEY AUTOINCREMENT,
                moderator   TEXT    NOT NULL,
                name        TEXT    NOT NULL UNIQUE
            );
        ''')
        conn.commit()
        conn.close()
    except:
        pass

def create_table_posts():
    try:    
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE POSTS(
                pid         INTEGER PRIMARY KEY AUTOINCREMENT,
                boardname   TEXT    NOT NULL,
                author      TEXT    NOT NULL,
                title       TEXT    NOT NULL,
                post_date   TEXT    NOT NULL,
                object      TEXT    NOT NULL, 
                cmt_object  TEXT    NOT NULL
            );
        ''')
        conn.commit()
        conn.close()
    except:
        pass

def create_table_mails():
    try:    
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE MAILS(
                mid         INTEGER PRIMARY KEY AUTOINCREMENT,
                sender      TEXT    NOT NULL,
                receiver    TEXT    NOT NULL,
                subject     TEXT    NOT NULL,
                mail_date   TEXT    NOT NULL,
                object      TEXT    NOT NULL
            );
        ''')
        conn.commit()
        conn.close()
    except:
        pass

def insert_user(username, email, password, bucket):
    # Return 0 if successfully inserted
    try:
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        params = (username, email, password, bucket)
        cursor = c.execute("INSERT INTO USERS (username, email, password, bucket) VALUES (?, ?, ?, ?)", params)
        conn.commit()
        conn.close()
        return 0
    except:
        pass
    return 1

def user_existed_check(username):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (username,)
    cursor = c.execute("SELECT COUNT(*) FROM USERS u WHERE u.username == ?", params)
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    return int(values[0]) > 0

def insert_board(moderator, name):
    # Return 0 if successfully inserted
    try:
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        params = (moderator, name,)
        cursor = c.execute("INSERT INTO BOARDS (moderator, name) VALUES (?, ?)", params)
        conn.commit()
        conn.close()
        return 0
    except:
        pass
    return 1

def board_existed_check(boardname):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (boardname,)
    cursor = c.execute("SELECT COUNT(*) FROM BOARDS b WHERE b.name == ?", params)
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    return int(values[0]) > 0

def insert_post(boardname, author, title, object_name, comment_object_name):
    # Return 0 if successfully inserted
    if board_existed_check(boardname):
        try:
            conn = sqlite3.connect('bbs.db')
            c = conn.cursor()
            cursor = c.execute("SELECT date('now')")
            post_date = cursor.fetchone()[0]
            params = (boardname, author, title, post_date, object_name, comment_object_name)
            cursor = c.execute("INSERT INTO POSTS (boardname, author, title, post_date, object, cmt_object) VALUES (?, ?, ?, ?, ?, ?)", params)
            conn.commit()
            conn.close()
            return 0
        except:
            pass
        return -1
    else:
        return 1

def post_existed_check(pid):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (pid,)
    cursor = c.execute("SELECT COUNT(*) FROM POSTS p WHERE p.pid == ?", params)
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    return int(values[0]) > 0

def insert_comment(pid):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (pid,)
    cursor = c.execute("SELECT author, cmt_object FROM POSTS p WHERE p.pid == ?", params)
    ret = cursor.fetchone()
    conn.commit()
    conn.close()
    return ret

def insert_mail(sender, receiver, subject, object_name):
    if user_existed_check(receiver):
        try:
            conn = sqlite3.connect('bbs.db')
            c = conn.cursor()
            cursor = c.execute("SELECT date('now')")
            mail_date = cursor.fetchone()[0]
            params = (sender, receiver, subject, mail_date, object_name)
            cursor = c.execute("INSERT INTO MAILS (sender, receiver, subject, mail_date, object) VALUES (?, ?, ?, ?, ?)", params)
            conn.commit()
            conn.close()
            return 0
        except:
            pass
        return -1
    else:
        return 1

def delete_mail(mid):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (mid,)
    cursor = c.execute("DELETE FROM MAILS WHERE mid == ?", params)
    conn.commit()
    conn.close()

def select_board(key = ""):
    ret = []
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = None
    if key == "":
        cursor = c.execute("SELECT * FROM BOARDS b")
    else:
        params = ("%" + key + "%",)
        cursor = c.execute("PRAGMA case_sensitive_like = true")
        cursor = c.execute("SELECT * FROM BOARDS b WHERE b.name LIKE ?", params)
    ret = cursor.fetchall()
    conn.commit()
    conn.close()
    return ret

def select_post(boardname = "", key = "", pid = -1):    
    ret = []
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = None
    if boardname != "":
        if key == "":
            params = (boardname,)
            cursor = c.execute("SELECT pid, title, author, post_date FROM POSTS p WHERE p.boardname == ?", params)
        else:
            params = (boardname, "%" + key + "%",)
            cursor = c.execute("PRAGMA case_sensitive_like = true")
            cursor = c.execute("SELECT pid, title, author, post_date FROM POSTS p WHERE p.boardname == ? AND p.title LIKE ?", params)
        ret = cursor.fetchall()
    elif pid != -1:
        params = (pid,)
        cursor = c.execute("SELECT author, title, post_date, object, cmt_object FROM POSTS p WHERE p.pid == ?", params)
        ret = cursor.fetchall()
    conn.commit()
    conn.close()
    return ret

def select_mail(receiver = ""):    
    ret = []
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = None
    params = (receiver,)
    cursor = c.execute("PRAGMA case_sensitive_like = true")
    cursor = c.execute("SELECT subject, sender, mail_date, object, mid FROM MAILS m WHERE m.receiver == ?", params)
    ret = cursor.fetchall()
    conn.commit()
    conn.close()
    return ret

def test():
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    
    print("USERS")
    cursor = c.execute("SELECT * FROM USERS")
    for a in cursor:
        print(a)

    print("BOARDS")
    cursor = c.execute("SELECT * FROM BOARDS")
    for a in cursor:
        print(a)

    conn.commit()
    conn.close()
    return

def create_all_tables():
    create_table_users()
    create_table_boards()
    create_table_posts()
    create_table_mails()

if __name__ == '__main__':
    create_all_tables()
    # create_table_users()
    # create_table_boards()
    # create_table_posts()
    # create_table_comments()
    # test()
    # insert_user("u1", "1@1", "111")
    # insert_user("u2", "1@1", "111")
    # insert_board("b1", "u1")
    # insert_board("b2", "u2")
    # insert_board("b3", "u3--illegal")
    # insert_post(1, "u1", "t1", "c1")
    # insert_post(2, "u1", "t2", "c2")
    # insert_post(3, "u4", "t3", "c3")
    # insert_post(4, "u1", "t4", "c4")
    # insert_post(2, "u1", "t4", "c4")
    # test()
    # res = select_board(key = "1")
    # for a in res:
    #     print(a)

    # res = select_post(bid = 2, key = "t")
    # for a in res:
    #     print(a)

    # delete_post(1, "execute")
    # insert_post(2, "u1", "t4", "c4")
    # insert_post(1, "u1", "t4", "c4")
    # insert_post(23, "u1", "t4", "c4")
    # update_post(pid=3, username="u1", title_or_content="--title", change="new1")
    # update_post(pid=3, username="u4", title_or_content="--title", change="new2")
    # update_post(pid=3, username="u4", title_or_content="--content", change="new3")
    # update_post(pid=3, username="u4", title_or_content="--title", change="new4")
    # update_post(pid=3, username="u2", title_or_content="--title", change="new5")
    # insert_comment(pid=1, user="u1", comment="111")
    # insert_comment(pid=1, user="u2", comment="222")
    # insert_comment(pid=3, user="u3", comment="333")
    # insert_comment(pid=3, user="u4", comment="444")
    # insert_comment(pid=4, user="u5", comment="555")
    # insert_comment(pid=6, user="u6", comment="666")
    # test()

    # print("COMMENTS")
    # conn = sqlite3.connect('bbs.db')
    # c = conn.cursor()
    # cursor = c.execute("SELECT * FROM COMMENTS")
    # for a in cursor:
    #     print(a)
    # conn.commit()
    # conn.close()

    # print(select_comment(pid=3))
    # print(select_comment(pid=4))
    # print(select_comment(pid=5))
    # print(select_comment(pid=6))

    # print(insert_user("test", "test@email", "pass"))  
    # print(login_check("test", "pass"))