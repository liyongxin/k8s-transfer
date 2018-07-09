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
    print arr[0]
