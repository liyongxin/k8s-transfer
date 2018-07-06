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

    print "SBss-dd123".lower()
    aaa=[]
    aaa.append(1)
    print aaa or "123"