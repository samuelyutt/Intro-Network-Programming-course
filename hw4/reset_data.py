import sqlite3, boto3
import db

def delete_post():
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = c.execute("SELECT author, object, cmt_object FROM POSTS p")
    results = cursor.fetchall()
    conn.commit()
    conn.close()

    print('Deleting post and comment objects')
    s3 = boto3.resource('s3')
    for row in results:
        bucket = db.get_bucket(row[0])
        target_bucket = s3.Bucket(bucket)
        target_object = target_bucket.Object(row[1])
        target_object.delete()
        target_bucket = s3.Bucket(bucket)
        target_object = target_bucket.Object(row[2])
        target_object.delete()

    print('Deleting table post from database')
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = c.execute("DROP TABLE POSTS")
    conn.commit()
    conn.close()


def delete_mail():
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = c.execute("SELECT receiver, object FROM MAILS")
    results = cursor.fetchall()
    conn.commit()
    conn.close()

    print('Deleting mail objects')
    s3 = boto3.resource('s3')
    for row in results:
        bucket = db.get_bucket(row[0])
        target_bucket = s3.Bucket(bucket)
        target_object = target_bucket.Object(row[1])
        target_object.delete()

    print('Deleting table mail from database')
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = c.execute("DROP TABLE MAILS")
    conn.commit()
    conn.close()

def delete_user():
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = c.execute("SELECT bucket FROM USERS")
    results = cursor.fetchall()
    conn.commit()
    conn.close()

    print('Deleting user buckets')
    s3 = boto3.resource('s3')
    for row in results:
        target_bucket = s3.Bucket(row[0])
        target_bucket.delete()

    print('Deleting table user from database')
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = c.execute("DROP TABLE USERS")
    conn.commit()
    conn.close()

def delete_board():
    print('Deleting table board from database')
    conn = sqlite3.connect('bbs.db')
    c = conn.cursor()
    cursor = c.execute("DROP TABLE BOARDS")
    conn.commit()
    conn.close()


if __name__ == '__main__':
    delete_post()
    delete_mail()
    delete_user()
    delete_board()
    print('Done')

