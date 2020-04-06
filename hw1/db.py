import sqlite3

def create_table():
    try:    
        conn = sqlite3.connect('bbs.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE USERS(
                UID INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT NOT NULL UNIQUE,
                Email TEXT NOT NULL,
                Password TEXT NOT NULL
            );
        ''')
        conn.commit()
        conn.close()
    except:
        pass

def user_existed(username):
    # Returns True if user is already exist
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (username,)
    cursor = c.execute("SELECT COUNT(*) FROM USERS u WHERE u.Username == ?", params)
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    return int(values[0]) > 0

def insert_user(username, email, password):
    if not user_existed(username):
        try:
            conn = sqlite3.connect('bbs.db')
            c = conn.cursor()
            params = (username, email, password,)
            cursor = c.execute("INSERT INTO USERS (Username, Email, Password) VALUES (?, ?, ?)", params)
            conn.commit()
            conn.close()
            # Success
            return 0
        except:
            pass
    # Fail
    return 1

def login_check(username, password):
    # Returns True if password matches username
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    params = (username, password, )
    cursor = c.execute("SELECT COUNT(*) FROM USERS u WHERE u.Username == ? AND u.Password == ?", params)
    values = cursor.fetchone()
    conn.commit()
    conn.close()
    return int(values[0]) > 0


if __name__ == '__main__':       
    create_table()
    # print(insert_user("test", "test@email", "pass"))  
    # print(login_check("test", "pass"))