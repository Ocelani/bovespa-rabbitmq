import pika
import os
import sys
import datetime
from LivroDeOfertas import LivroDeOfertas


def main():
    # connection
    server = sys.argv[1] if len(
        sys.argv) > 1 else 'amqps://CLOUDAMQP_URL'
    url = os.environ.get('CLOUDAMQP_URL',
                         server)
    params = pika.URLParameters(url)
    params.socket_timeout = 5
    connection = pika.BlockingConnection(params)

    # channel
    broker_channel = connection.channel()
    bolsa_channel = connection.channel()

    # exchange
    broker_channel.exchange_declare(exchange='BROKER', exchange_type='topic')
    bolsa_channel.exchange_declare(exchange='BOLSADEVALORES', exchange_type='topic')

    # queues
    broker_channel.queue_declare(queue='broker_q')

    # consume
    broker_channel.queue_bind(exchange='BROKER', queue='broker_q', routing_key='#')

    print('Bolsa de Valores de São Paulo. \n' + str(datetime.datetime.now()))

    ofertas = LivroDeOfertas()

    def callback(ch, method, properties, body):
        print(" [x] %r:%r" % (method.routing_key, body))
        # publish
        ordem = ofertas.new_ordem(method.routing_key, body)
        message = ordem.get_message()
        bolsa_channel.basic_publish(exchange='BOLSADEVALORES', routing_key=method.routing_key, body=message)
        transacao = ofertas.make_transaction(ordem)
        if transacao:
            bolsa_channel.basic_publish(exchange='BOLSADEVALORES', routing_key=transacao.get_routing_key(),
                                        body=transacao.get_message())

    broker_channel.basic_consume(queue='broker_q', on_message_callback=callback, auto_ack=True)

    broker_channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
