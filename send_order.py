# envio do pedido
from pprint import pprint
from sales_class import Sales
from order_class import Order
from auth_sheet import SheetGoogle


with Order() as o:
    o.add_header("Assai")
    o.resume["discountValue"] = 10

o.add_item("mussarela", 10, 1.3, "10")
o.add_item("parmesão", 1, 100, "10%")
o.add_item("manteiga", 15, 2)
o.add_item("provolone", 3, 17.3)
o.cancel_item(1)
o.apply_discount(scope="resume")
#pprint(o.item)

with Sales() as s:
    s.company = "Litoral Vale"
    s.messagerID = "123456789"
    s.add_order(o)

lines = list(map(lambda l: list(l.values()), o.item))
titles = list(map(lambda l: list(l.keys()), o.item))[0]
header = []
for k, v in o.header.items():
    header.append(k)
    header.append(v)
resume = []
for k, v in o.resume.items():
    resume.append(k)
    resume.append(v)

#pprint(header)
#pprint(titles)
pprint(lines)
pprint(resume)
#header = []
#lines = []
#titles = []
#footer = []
#planilha = SheetGoogle()

#planilha.add_sheet_values(o.header["customer"],
#title=titles,
#line=lines,
#hdr=header,
#foot=resume)

#pprint(planilha.spreadsheet)
#pprint(planilha.sheet)
