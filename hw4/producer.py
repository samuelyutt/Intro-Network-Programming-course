from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
future = producer.send('test', key=b'12345', value=b'abcde')
result = future.get(timeout=10)
print(result)