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

    for i in range(10):
        time.sleep(2)
        print i
        if i == 2:
            break
    print "hshhsh"