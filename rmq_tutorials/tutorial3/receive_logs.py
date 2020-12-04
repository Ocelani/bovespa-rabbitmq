import pika
import os

# connection
url = os.environ.get('CLOUDAMQP_URL',
                     'amqps://CLOUDAMQP_URL')
params = pika.URLParameters(url)
params.socket_timeout = 5
connection = pika.BlockingConnection(params)

# channel
channel = connection.channel()

# exchange
channel.exchange_declare(exchange='logs', exchange_type='fanout')

# default queue ' '
result = channel.queue_declare(queue='', exclusive=True)  # exclusive: it's gonna be deleted once the client disconnects
queue_name = result.method.queue  # gets queue (random) name

channel.queue_bind(exchange='logs', queue=queue_name)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r" % body)


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
