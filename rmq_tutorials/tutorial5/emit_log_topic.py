import os
import pika
import sys

# connection
url = os.environ.get('CLOUDAMQP_URL',
                     'amqps://CLOUDAMQP_URL')
params = pika.URLParameters(url)
params.socket_timeout = 5
connection = pika.BlockingConnection(params)

# channel
channel = connection.channel()

# declare exchange, of type fanout (broadcast)
channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

routing_key = sys.argv[1] if len(sys.argv) > 2 else 'anonymous.info'
message = ' '.join(sys.argv[1:]) or "info: Hello World!"

channel.basic_publish(exchange='topic_logs', routing_key=routing_key, body=message)
print(" [x] Sent %r:%r" % (routing_key, message))

connection.close()
