# estrutura do pedido
from datetime import datetime, timedelta


class Order(object):

    def __init__(self):

        super(Order, self).__init__()

        order_num = "{}{}{}{}{}".format(str(datetime.today().year),
        str(datetime.today().month).zfill(2),
        str(datetime.today().day).zfill(2),
        str(datetime.today().hour).zfill(2),
        str(datetime.today().minute).zfill(2))

        header = {"customer": None,
        "orderNumber": order_num,
        "orderDate": datetime.today().strftime("%d/%m/%Y %H:%M"),
        "deliveryDate": (datetime.today() +
        timedelta(days=7)).strftime("%d/%m/%Y %H:%M")}

        resume = {"quantityItem": 0,
        "discountValue": 0,
        "discountType": None,
        "totalOrder": 0}

        order = {"header": header,
        "item": list(),
        "resume": resume,
        "billed": False,
        "canceled": False}

        self.__dict__ = order

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def add_header(self, customer_name):
        try:
            self.header["customer"] = customer_name
        except Exception as e:
            raise Exception("Erro ao listar item: {}".format(e))

    def add_item(self, *args):
        try:
            if (args[0] is None):
                raise Exception("Produto não informado")
            else:
                product = args[0]

            if (args[1] is None):
                raise Exception("Quantidade não informada")
            else:
                amount = args[1]

            if (args[2] is None):
                raise Exception("Valor Unitário não informado")
            else:
                vl_unit = args[2]

            vl_discount = 0
            tp_discount = None
            if (len(args) > 3):
                if (args[3] is None):
                    vl_discount = 0
                else:
                    tp_discount = ""
                    vl_discount = args[3]
                    if ("%" in vl_discount):
                        tp_discount = args[3][-1]
                        vl_discount = args[3][0:len(vl_discount) - 1].strip()
                    vl_discount = float(vl_discount)

            vl_item = (amount * vl_unit)

        except Exception as e:
            raise Exception("Erro ao criar item: {}".format(e))
        else:
            try:
                item = {"number": len(self.item) + 1,
                "canceled": False,
                "product": product,
                "amount": amount,
                "unitValue": vl_unit,
                "discountValue": vl_discount,
                "discountType": tp_discount,
                "totalItem": vl_item}

                self.item.append(item)

                vl_item = self.apply_discount(scope="item",
                item_number=(len(self.item) - 1))
                self.resume["totalOrder"] += vl_item
                self.resume["quantityItem"] += 1

            except Exception as e:
                raise Exception("Erro ao atualizar pedido: {}".format(e))

    def cancel_item(self, item_number):
        canceled = self.item[item_number]["canceled"]
        self.item[item_number]["canceled"] = not(canceled)
        self.resume["totalOrder"] = self.apply_discount(scope="resume")

    def apply_discount(self, scope, item_number=0):
        try:
            if (scope == "item"):
                i = item_number
                vl_total = self.item[i]["unitValue"] * self.item[i]["amount"]
                tp_discount = self.item[i]["discountType"]
                vl_discount = self.item[i]["discountValue"]
                if (tp_discount is not None) and (vl_discount is not None):
                    if (tp_discount == "%") and (vl_discount > 0):
                        vl_discount = (vl_total * (vl_discount / 100))
                if (vl_discount is None):
                    vl_discount = 0

                self.item[i]["totalItem"] = vl_total - vl_discount

                return self.item[i]["totalItem"]
            else:
                vl_item = 0
                for i in self.item:
                    if (not i["canceled"]):
                        item_num = i["number"] - 1
                        vl_item += self.apply_discount(scope="item",
                        item_number=item_num)
                    else:
                        self.resume["quantityItem"] -= 1

                tp_discount = self.resume["discountType"]
                vl_discount = self.resume["discountValue"]
                if (tp_discount is not None) and (vl_discount is not None):
                    if (tp_discount == "%") and (vl_discount > 0):
                        vl_discount = (vl_total * (vl_discount / 100))
                if (vl_discount is None):
                    vl_discount = 0
                self.resume["totalOrder"] = vl_item - vl_discount
                return self.resume["totalOrder"]
        except Exception as e:
            raise Exception("Erro ao calcular desconto: {}".format(e))
