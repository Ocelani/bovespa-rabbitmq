import os
import pika
import sys

# connection
url = os.environ.get('CLOUDAMQP_URL',
                     'amqps://CLOUDAMQP_URL')
params = pika.URLParameters(url)
params.socket_timeout = 5
connection = pika.BlockingConnection(params)
channel = connection.channel()

# specifies queue
channel.queue_declare(queue='task_queue', durable=True)  # durable: the queue persists if the server restarts

message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                          delivery_mode=2,  # make message persistent
                      ))
print(" [x] Sent %r" % message)
connection.close()
