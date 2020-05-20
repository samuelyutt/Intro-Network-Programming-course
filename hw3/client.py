import sys, socket
import boto3


PORT = 7788  # socket server port number

if len(sys.argv) == 2:
    PORT = int(sys.argv[1])

host = socket.gethostname()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, PORT))

data = ''
s3 = boto3.resource('s3')
# while message.lower().strip() != 'bye':
while data != 'exit':

    msg = client.recv(1024).decode()
    if '&<!register::>' in msg:
        msg = msg.split('&<!register::>')[1]
        metadata = msg.split('&<!meta|msg>')[0].split('&<!spl>')
        msg = msg.split('&<!meta|msg>')[1]
        
        bucket = metadata[0]
        
        s3.create_bucket(Bucket = bucket)
    elif '&<!create-post>' in msg:
        msg = msg.split('&<!create-post>')[1]
        matadata = msg.split('&<!meta|msg>')[0].split('&<!spl>')
        msg = msg.split('&<!meta|msg>')[1]

        bucket = matadata[0]
        object_name = matadata[1]
        content = matadata[2]
        comment_object_name = matadata[3]      
        
        file = open('./tmp/' + object_name, 'w')
        file.write(content)
        file.close()
        target_bucket = s3.Bucket(bucket)
        target_bucket.upload_file('./tmp/' + object_name, object_name)

        file = open('./tmp/' + comment_object_name, 'w')
        file.write('\n--')
        file.close()
        target_bucket = s3.Bucket(bucket)
        target_bucket.upload_file('./tmp/' + comment_object_name, comment_object_name)
    elif '&<!update-post-content>' in msg:
        msg = msg.split('&<!update-post-content>')[1]
        matadata = msg.split('&<!meta|msg>')[0].split('&<!spl>')
        msg = msg.split('&<!meta|msg>')[1]

        bucket = matadata[0]
        object_name = matadata[1]
        content = matadata[2]

        file = open('./tmp/' + object_name, 'w')
        file.write(content)
        file.close()
        target_bucket = s3.Bucket(bucket)
        target_bucket.upload_file('./tmp/' + object_name, object_name)
    elif '&<!delete-post::>' in msg:
        msg = msg.split('&<!delete-post::>')[1]
        matadata = msg.split('&<!meta|msg>')[0].split('&<!spl>')
        msg = msg.split('&<!meta|msg>')[1]

        bucket = matadata[0]
        object_name = matadata[1]
        comment_object_name = matadata[2] 

        target_bucket = s3.Bucket(bucket)
        target_object = target_bucket.Object(object_name)
        target_object.delete()
        target_bucket = s3.Bucket(bucket)
        target_object = target_bucket.Object(comment_object_name)
        target_object.delete()
    elif '&<!read::>' in msg:
        msg = msg.split('&<!read::>')[1]
        matadata = msg.split('&<!meta|msg>')[0].split('&<!spl>')
        msg = msg.split('&<!meta|msg>')[1]

        bucket = matadata[0]
        object_name = matadata[1] 
        comment_object_name = matadata[2]        
        
        target_bucket = s3.Bucket(bucket)
        target_object = target_bucket.Object(object_name)
        object_content = target_object.get()['Body'].read().decode()
        msg += object_content

        target_bucket = s3.Bucket(bucket)
        target_object = target_bucket.Object(comment_object_name)
        object_content = target_object.get()['Body'].read().decode()
        msg += object_content
    elif '&<!comment>' in msg:
        msg = msg.split('&<!comment>')[1]
        matadata = msg.split('&<!meta|msg>')[0].split('&<!spl>')
        msg = msg.split('&<!meta|msg>')[1]

        bucket = matadata[0]
        comment_object_name = matadata[1]
        comment = matadata[2]

        target_bucket = s3.Bucket(bucket)
        target_object = target_bucket.Object(comment_object_name)
        object_content = target_object.get()['Body'].read().decode()
        file = open('./tmp/' + comment_object_name, 'w')
        file.write(object_content + '\n' + comment)
        file.close()
        target_bucket = s3.Bucket(bucket)
        target_bucket.upload_file('./tmp/' + comment_object_name, comment_object_name)
    elif '&<!mail-to>' in msg:
        msg = msg.split('&<!mail-to>')[1]
        matadata = msg.split('&<!meta|msg>')[0].split('&<!spl>')
        msg = msg.split('&<!meta|msg>')[1]

        bucket = matadata[0]
        object_name = matadata[1]
        content = matadata[2]

        file = open('./tmp/' + object_name, 'w')
        file.write(content)
        file.close()
        target_bucket = s3.Bucket(bucket)
        target_bucket.upload_file('./tmp/' + object_name, object_name)
    elif '&<!retr-mail::>' in msg:
        msg = msg.split('&<!retr-mail::>')[1]
        matadata = msg.split('&<!meta|msg>')[0].split('&<!spl>')
        msg = msg.split('&<!meta|msg>')[1]

        bucket = matadata[0]
        object_name = matadata[1]

        target_bucket = s3.Bucket(bucket)
        target_object = target_bucket.Object(object_name)
        object_content = target_object.get()['Body'].read().decode()
        msg += object_content
    elif '&<!delete-mail::>' in msg:
        msg = msg.split('&<!delete-mail::>')[1]
        matadata = msg.split('&<!meta|msg>')[0].split('&<!spl>')
        msg = msg.split('&<!meta|msg>')[1]

        bucket = matadata[0]
        object_name = matadata[1]

        target_bucket = s3.Bucket(bucket)
        target_object = target_bucket.Object(object_name)
        target_object.delete()
    
    if msg != ' ':
        print(msg)
    
    print('% ', end='')
    data = input()
    data = data if data else ' '
    client.send(data.encode())

client.close()