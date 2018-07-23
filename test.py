import time
import json
from decimal import *

if __name__ == '__main__':
    url = "www.ddd.com/?aaa=1&b=2"
    if url.count("?") > 0:
        print url + "&project_name=alauda"
    else:
        print url + "?project_name=alauda"

    aaa = Decimal(0.125)/Decimal('3')
    aaa = 2043
    c = round(aaa, 4)
    print type(c)
    print float(aaa)
    print type(aaa)
    print str(aaa)
    ste = "[\"bin\", \"sh\"]"
    if ste.startswith("[") and ste.endswith("]"):
        arr = json.loads(ste)

    hhh = "duplicate key value violates unique constraint alery exiets"
    print hhh.find("duplicate key value violates unique constraint")
    args = "www.baidu.cn www.c.cn"
    print args.split(" ")
    print hhh.lower()

    sum = 0
    for i in range(1, 101):
        if i % 2 == 0:
            sum += i
    print sum

    hh = 2
    is_app = True if hh > 3 else False
    print is_app