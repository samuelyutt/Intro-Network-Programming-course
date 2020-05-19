import sys, socket
import boto3


PORT = 7788  # socket server port number

if len(sys.argv) == 2:
    PORT = int(sys.argv[1])

host = socket.gethostname()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, PORT))

data = ''
# while message.lower().strip() != 'bye':
while data != 'exit':

    msg = client.recv(1024).decode()
    if '<!read::>' in msg:
        msg = msg.split('<!read::>')[1]
        matadata = msg.split('<!metadata|content>')[0]
        bucket = matadata.split('<!bucket|object>')[0]
        object_name = matadata.split('<!bucket|object>')[1]
        msg = msg.split('<!metadata|content>')[1]
        s3 = boto3.resource('s3')
        target_bucket = s3.Bucket(bucket)
        target_object = target_bucket.Object(object_name)
        object_content = target_object.get()['Body'].read().decode()
        msg += object_content
    if msg != ' ':
        print(msg)
    print('% ', end='')
    data = input()
    data = data if data else ' '
    client.send(data.encode())

client.close()