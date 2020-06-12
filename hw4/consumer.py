import threading
import time
from kafka import KafkaConsumer

def consume():
    consumer = KafkaConsumer(group_id='123', bootstrap_servers=['localhost:9092'])
    while True:
        topic = ['test']
        consumer.subscribe(topics=topic)
        msg = consumer.poll(5)
        if msg:
            print(msg)


if __name__ == '__main__':
    t = threading.Thread(target=consume)
    t.start()
    t.join()