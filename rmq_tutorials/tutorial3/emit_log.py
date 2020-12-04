import os
import pika
import sys

# connection
url = os.environ.get('CLOUDAMQP_URL',
                     'amqps://CLOUDAMQP_URL')
params = pika.URLParameters(url)
params.socket_timeout = 5
connection = pika.BlockingConnection(params)

#channel
channel = connection.channel()

# declare exchange, of type fanout (broadcast)
channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = ' '.join(sys.argv[1:]) or "info: Hello World!"
channel.basic_publish(exchange='logs', routing_key='', body=message)
print(" [x] Sent %r" % message)

connection.close()
