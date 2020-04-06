import sqlite3

def create_table():
    try:
        c.execute('''
            CREATE TABLE USERS(
                UID INTEGER PRIMARY KEY AUTOINCREMENT,
                Username TEXT NOT NULL UNIQUE,
                Email TEXT NOT NULL,
                Password TEXT NOT NULL
            );
        ''')
    except:
        pass

def user_existed(username):
    params = (username,)
    cursor = c.execute("SELECT COUNT(*) FROM USERS u WHERE u.Username == ?", params)
    values = cursor.fetchone()
    return int(values[0]) > 0

def insert_user(username, email, password):
    if not user_existed(username):
        try:
            params = (username, email, password,)
            cursor = c.execute("INSERT INTO USERS (Username, Email, Password) VALUES (?, ?, ?)", params)
            # Success
            return 0
        except:
            pass
    # Fail
    return 1

def login_check(username, password):
    params = (username, password, )
    cursor = c.execute("SELECT COUNT(*) FROM USERS u WHERE u.Username == ? AND u.Password == ?", params)
    values = cursor.fetchone()
    return int(values[0]) > 0



if __name__ == '__main__':   
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    
    create_table()
    # print(insert_user("test", "test@email", "pass"))    
    # print(user_existed("test"))      
    print(login_check("test", "pass"))

    conn.commit()
    conn.close()