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

def delete_post_check(pid, username):
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

def delete_post(pid, username):
    check_err = delete_post_check(pid, username)
    if not check_err:
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        params = (pid, username, )
        cursor = c.execute("DELETE FROM POSTS WHERE pid == ? AND author == ?", params)
        conn.commit()
        conn.close()
    print(check_err)
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
                password    TEXT    NOT NULL
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
                board_id    INTEGER NOT NULL,
                author      TEXT    NOT NULL,
                title       TEXT    NOT NULL,
                post_date   TEXT    NOT NULL,
                content     TEXT    NOT NULL,
                FOREIGN KEY(board_id)  REFERENCES BOARDS(bid)
            );
        ''')
        conn.commit()
        conn.close()
    except:
        pass

def insert_user(username, email, password):
    # Return 0 if successfully inserted
    try:
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        params = (username, email, password,)
        cursor = c.execute("INSERT INTO USERS (username, email, password) VALUES (?, ?, ?)", params)
        conn.commit()
        conn.close()
        return 0
    except:
        pass
    return 1

def insert_board(name, moderator):
    # Return 0 if successfully inserted
    try:
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        params = (name, moderator,)
        cursor = c.execute("INSERT INTO BOARDS (name, moderator) VALUES (?, ?)", params)
        conn.commit()
        conn.close()
        return 0
    except:
        pass
    return 1

def board_existed_check(bid):
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (bid,)
    cursor = c.execute("SELECT COUNT(*) FROM BOARDS b WHERE b.bid == ?", params)
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    return int(values[0]) > 0

def insert_post(bid, author, title, content):
    # Return 0 if successfully inserted
    if board_existed_check(bid):
        try:
            conn = sqlite3.connect('bbs.db')
            c = conn.cursor()
            cursor = c.execute("SELECT date('now')")
            post_date = cursor.fetchone()[0]
            params = (bid, author, title, post_date, content,)
            cursor = c.execute("INSERT INTO POSTS (board_id, author, title, post_date, content) VALUES (?, ?, ?, ?, ?)", params)
            conn.commit()
            conn.close()
            return 0
        except:
            pass
        return -1
    else:
        return 1

def select_board(key = ""):
    ret = []
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = None
    if key == "":
        cursor = c.execute("SELECT * FROM BOARDS b")
    else:
        params = ("%" + key + "%",)
        cursor = c.execute("SELECT * FROM BOARDS b WHERE b.name LIKE ?", params)
    ret = cursor.fetchall()
    conn.commit()
    conn.close()
    return ret

def select_post(bid = -1, key = "", pid = -1):    
    ret = []
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = None
    if bid != -1:
        if key == "":
            params = (bid,)
            cursor = c.execute("SELECT pid, author, title, post_date, content FROM POSTS p WHERE p.board_id == ?", params)
        else:
            params = (bid, "%" + key + "%",)
            cursor = c.execute("SELECT pid, author, title, post_date, content FROM POSTS p WHERE p.board_id == ? AND p.title LIKE ?", params)
        ret = cursor.fetchall()
    elif pid != -1:
        params = (pid,)
        cursor = c.execute("SELECT author, title, post_date, content FROM POSTS p WHERE p.pid == ?", params)
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

    print("POSTS")
    cursor = c.execute("SELECT * FROM POSTS")
    for a in cursor:
        print(a)

    conn.commit()
    conn.close()
    return


if __name__ == '__main__':       
    create_table_users()
    create_table_boards()
    create_table_posts()
    # test()
    insert_user("u1", "1@1", "111")
    insert_user("u2", "1@1", "111")
    insert_board("b1", "u1")
    insert_board("b2", "u2")
    insert_board("b3", "u3--illegal")
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
    insert_post(2, "u1", "t4", "c4")
    insert_post(1, "u1", "t4", "c4")
    insert_post(23, "u1", "t4", "c4")
    test()
    # print(insert_user("test", "test@email", "pass"))  
    # print(login_check("test", "pass"))