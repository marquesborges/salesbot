# estrutura do vendedor


class Sales(object):

    def __init__(self):
        super(Sales, self).__init__()

        sales = {"company": None,
        "messagerID": None,
        "orders": list()}

        self.__dict__ = sales

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def add_order(self, order):
        self.orders.append(order)

    def cancel_order(self, order_number):
        try:
            order_list = list(filter(lambda o: o.orderNumber == order_number,
            self.orders))
            for o in order_list:
                if (o.billed):
                    raise Exception("Não pode cancelar pedido transmitido")
                o.canceled = not(o.canceled)
        except Exception as e:
            raise Exception("Erro ao cancelar pedido: {}".format(e))
