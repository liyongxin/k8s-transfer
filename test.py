import time

if __name__ == '__main__':
    url = "www.ddd.com/?aaa=1&b=2"
    if url.count("?") > 0:
        print url + "&project_name=alauda"
    else:
        print url + "?project_name=alauda"

    ips = []
    ips.append("aaa")
    ips.append("vvv")
    print ",".join(ips)

    print "begin {}".format("" or "default")

    aa = {
        "key1": 1,
        "key2": 2

    }
    print aa
    del aa["key2"]
    print aa