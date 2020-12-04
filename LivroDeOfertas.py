import datetime


def read_ordem(routing_key, body):

    body = body.decode('ascii')

    tipo, ativo = routing_key.split('.')
    body = str(body)
    quant, val, broker = body.split(',')
    quant = int(quant.split(':')[1])
    val = float(val.split(':')[1])
    broker = broker.split(':')[1][0:4]  # gets 4 first chars from string
    return tipo, ativo, quant, val, broker


class Ordem:
    def __init__(self, tipo, ativo, quant, val, broker):

        self.tipo = tipo
        self.quant = quant
        self.val = val
        self.ativo = ativo
        self.broker = broker

    def get_message(self):
        return "quant:" + str(self.quant) + ",val:" + str(self.val) + ",broker:" + str(self.broker)

    def get_routing_key(self):
        return self.tipo + "." + self.ativo


class Transacao:

    def __init__(self, ativo, corr_vd, corr_cp, quant, val, date=str(datetime.datetime.now())):
        self.date = date
        self.ativo = ativo
        self.corr_vd = corr_vd
        self.corr_cp = corr_cp
        self.quant = quant
        self.val = val

    def get_message(self):
        return "data-hora:" + str(self.date) + ",corr_vd:" + self.corr_vd + ",corr_cp:" + self.corr_cp + ",quant:" + \
               str(self.quant) + ",val:" + str(self.val)

    def get_routing_key(self):
        return "transacao." + self.ativo


class LivroDeOfertas:

    def __init__(self):
        self.ordem_compra = []
        self.ordem_venda = []  # implementar persistencia
        self.transactions = []

    '''def new_ordem(self, tipo, ativo, quant, val, broker):
        ordem = Ordem(tipo, ativo, quant, val, broker)

        if ordem.tipo == 'compra':
            self.ordem_compra.append(ordem)
        else:
            self.ordem_venda.append(ordem)

        return ordem'''

    def new_ordem(self, routing_key, body):
        tipo, ativo, quant, val, broker = read_ordem(routing_key, body)
        ordem = Ordem(tipo, ativo, quant, val, broker)

        if ordem.tipo == 'compra':
            self.ordem_compra.append(ordem)
        else:
            self.ordem_venda.append(ordem)

        return ordem

    def make_transaction(self, ordem):
        transacao = None
        if ordem.tipo == 'compra':
            sublist = [o for o in self.ordem_venda if o.ativo == ordem.ativo]
            sign = 1
        else:
            sublist = [o for o in self.ordem_compra if o.ativo == ordem.ativo]  # sublist com os mesmos ativos
            sign = -1
        for o in sublist:
            if ordem.val * sign == sign * o.val:  # sign inverte o sinal conforme ordem é de compra ou venda
                n_lotes = min(ordem.quant, o.quant)
                if ordem.tipo == 'compra':
                    i = self.ordem_compra.index(ordem)
                    self.ordem_compra.__getitem__(i).quant -= n_lotes
                    i = self.ordem_venda.index(o)
                    self.ordem_venda.__getitem__(i).quant -= n_lotes
                    corr_vd, corr_cp = o.broker, ordem.broker
                else:
                    i = self.ordem_compra.index(o)
                    self.ordem_compra.__getitem__(i).quant -= n_lotes
                    i = self.ordem_venda.index(ordem)
                    self.ordem_venda.__getitem__(i).quant -= n_lotes
                    corr_vd, corr_cp = ordem.broker, o.broker,
                transacao = Transacao(ordem.ativo, corr_vd, corr_cp, n_lotes, ordem.val)
                self.transactions.append(transacao)
                self.ordem_venda = list(filter(lambda x: x.quant == 0, self.ordem_venda))  # filtra as ordens de qtd = 0
                self.ordem_compra = list(filter(lambda x: x.quant == 0, self.ordem_compra))
        return transacao

    def update_transaction(self, routing_key, body):
        tipo, ativo = routing_key.split('.')
        body = str(body)
        date, corr_vd, corr_cp, quant, val = body.split(',')
        date = date.split(':')[1]
        corr_vd = corr_vd.split(':')[1]
        corr_cp = corr_cp.split(':')[1]
        quant = int(quant.split(':')[1])
        val = float(val.split(':')[1].split("'")[0])

        venda = [o for o in self.ordem_venda if o.ativo == ativo and o.val == val and o.broker == corr_vd]
        if venda:
            venda[0].quant -= quant

        compra = [o for o in self.ordem_compra if o.ativo == ativo and o.val == val and o.broker == corr_cp]
        if compra:
            compra[0].quant -= quant

        self.ordem_venda = list(filter(lambda x: x.quant == 0, self.ordem_venda))  # filtra as ordens de qtd = 0
        self.ordem_compra = list(filter(lambda x: x.quant == 0, self.ordem_compra))

    '''def update_transaction(self, routing_key, body):
            tipo, ativo = routing_key.split('.')
            body = str(body)
            date, corr_vd, corr_cp, quant, val = body.split(',')
            date = date.split(':')[1]
            corr_vd = corr_vd.split(':')[1]
            corr_cp = corr_cp.split(':')[1]
            quant = int(quant.split(':')[1])
            val = float(val.split(':')[1].split("'")[0])

            transacao = Transacao(ativo, date, corr_vd, corr_cp, quant, val)
            self.transactions.append(transacao)

            compra = Ordem(tipo='compra', ativo=ativo, quant=quant, val=val, broker=corr_cp)  # vai dar pau se o val for diferente!!!
            venda = Ordem(tipo='venda', ativo=ativo, quant=quant, val=val, broker=corr_vd)
            i = self.ordem_compra.index(compra)
            self.ordem_compra.__getitem__(i).quant -= quant
            i = self.ordem_venda.index(venda)
            self.ordem_venda.__getitem__(i).quant -= quant

            self.ordem_venda = list(filter(lambda x: x.quant == 0, self.ordem_venda))  # filtra as ordens de qtd = 0
            self.ordem_compra = list(filter(lambda x: x.quant == 0, self.ordem_compra))'''

