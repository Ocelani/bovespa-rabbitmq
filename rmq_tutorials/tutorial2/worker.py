import pika
import sys
import os
import time


def main():
    # connection
    url = os.environ.get('CLOUDAMQP_URL',
                         'amqps://CLOUDAMQP_URL')
    params = pika.URLParameters(url)
    params.socket_timeout = 5
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # creating a queue is idempotent
    channel.queue_declare(queue='task_queue', durable=True)  # durable: the queue persists if the server restarts

    # recebe a mensagem via callback, passado por parâmetro
    def callback(ch, method, properties, body):
        print(" [x] Received %r" % body.decode())
        time.sleep(body.count(b'.'))
        print(" [x] Done")
        ch.basic_ack(delivery_tag=method.delivery_tag)  # acknowledgement

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue',
                          auto_ack=False, # auto acknowledgement false
                          on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
