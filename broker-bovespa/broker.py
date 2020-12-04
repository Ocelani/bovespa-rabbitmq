import os
import pika
import sys
import argparse

from LivroDeOfertas import LivroDeOfertas


parser = argparse.ArgumentParser(description='Process some integers.')

parser.add_argument('broker_name', action="store", type=str, help="nome da corretora usuário.")

parser.add_argument('--server', '-s', type=str, action='store',
                    default='amqps://CLOUDAMQP_URL',
                    help='RabbitMQ server URI')

parser.add_argument('--ordem', '-o', nargs=4, action='store',
                    help='4 arguments expected: compra/venda, ativo, quant, val',
                    required=True)

results = parser.parse_args()
server = results.server
tipo, ativo, quant, val = results.ordem[0], results.ordem[1], results.ordem[2], results.ordem[3]

rk = tipo + '.' + ativo
m = "quant:" + quant + ",val:" + val + ",corretora:" + results.broker_name
# print(results)


def main():
    # connection
    url = os.environ.get('CLOUDAMQP_URL', results.server)
    params = pika.URLParameters(url)
    params.socket_timeout = 5
    connection = pika.BlockingConnection(params)

    # channel
    broker_channel = connection.channel()
    bolsa_channel = connection.channel()

    # exchange
    broker_channel.exchange_declare(exchange='BROKER', exchange_type='topic')
    bolsa_channel.exchange_declare(exchange='BOLSADEVALORES', exchange_type='topic')

    # publish
    routing_key = rk
    message = m

    broker_channel.basic_publish(exchange='BROKER', routing_key=routing_key, body=message)
    print(" [x] Sent %r:%r" % (routing_key, message))
    # print("binding k: " + binding_key)

    # consume
    receive = bolsa_channel.queue_declare(queue='', exclusive=True)
    queue_name = receive.method.queue  # gets queue (random) name

    binding_keys = sys.argv[2:]  # substituir por um arquivo depois (BINDING KEYS PERTINENTES)
    bolsa_channel.queue_bind(exchange='BOLSADEVALORES', queue=queue_name, routing_key='*.*')

    ofertas = LivroDeOfertas()

    def callback(ch, method, properties, body):
        if method.routing_key.split('.')[0] == 'transacao':
            ofertas.update_transaction(method.routing_key, body)
        else:
            ofertas.new_ordem(method.routing_key, body)
        print(" [x] %r:%r" % (method.routing_key, body))

    bolsa_channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

    bolsa_channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
