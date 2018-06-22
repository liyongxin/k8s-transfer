import os
import json
import consts
from utils import utils


sys_ns = [
    "kube-public",
    "kube-system",
    "default"
]


def get_k8s_namespaces():
    all_ns_json = os.popen(consts.GET_ALL_NS_JSON).read()
    all_ns = json.loads(all_ns_json)
    res = []
    for item in all_ns['items']:
        ns = item['metadata']['name']
        if ns not in sys_ns:
            res.append(ns)
    return res


def get_alauda_namespaces():
    ns = utils.send_request("GET", consts.URLS["create_get_ns"] + "?page=1&page_size=100&cluster=" + consts.Configs["region_name"])
    return ns["results"]


def get_alauda_ns_by_name(ns_name):
    ns_list = get_alauda_namespaces()
    for ns in ns_list:
        resource = ns["resource"]
        print resource
        if resource["name"] == ns_name:
            return resource
    raise Exception("Error: find no namespace match for {}".format(ns_name))


def sync_ns_bak():
    region_id = utils.get_region_info("id")
    k8_ns = get_k8s_namespaces()
    for ns in k8_ns:
        req_params = {
            "cluster": {
                "uuid": region_id,
                "name": consts.Configs["region_name"]
            },
            "resource": {
                "name": ns
            }
        }
        print "begin sync namespace {} from k8s to alauda metadata".format(ns)
        utils.send_request("POST", consts.URLS["create_get_ns"], req_params)


def sync_ns():
    region_id = utils.get_region_info("id")
    resource_ns = utils.send_request("GET", consts.URLS["get_resource_ns"])
    for ns in resource_ns:
        req_params = {
            "cluster": {
                "uuid": region_id,
                "name": consts.Configs["region_name"]
            },
            "resource": {
                "name": "default--" + ns["name"]
            }
        }
        print "begin sync namespace {} ".format(ns["name"])
        utils.send_request("POST", consts.URLS["create_get_ns"], req_params)


if __name__ == '__main__':
    pass
