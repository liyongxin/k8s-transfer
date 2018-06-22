import json
import consts
import namespaces
from os import path
from utils import utils


def init_v1_apps(results=None):
    if results is None:
        results = []
    file_name = consts.Prefix["service_list_file"]
    svc_list = utils.send_request('GET', consts.URLS['get_svc_list'])
    print svc_list
    results.extend(svc_list['results'])
    # has to be len(svc_list['results']), not svc_list['count']
    if len(svc_list['results']) > 100:
        init_v1_apps(results)
    writer = open(file_name, "w")
    writer.write(json.dumps(results))
    writer.close()


def trans_v1_apps():
    pass


if __name__ == '__main__':
    pass
