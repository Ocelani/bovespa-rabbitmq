import pika
import os
import sys

# connection
url = os.environ.get('CLOUDAMQP_URL',
                     'amqps://CLOUDAMQP_URL')
params = pika.URLParameters(url)
params.socket_timeout = 5
connection = pika.BlockingConnection(params)

# channel
channel = connection.channel()

# exchange
channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

# default queue ' '
result = channel.queue_declare(queue='', exclusive=True)  # exclusive: it's gonna be deleted once the client disconnects
queue_name = result.method.queue  # gets queue (random) name

binding_keys = sys.argv[1:]
if not binding_keys:
    sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
    sys.exit(1)


for binding_key in binding_keys:
    channel.queue_bind(exchange='topic_logs', queue=queue_name, routing_key=binding_key)

print(' [*] Waiting for logs. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] %r:%r" % (method.routing_key, body))


channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
