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
    return all_ns['items']


def get_k8s_ns_by_name(k8s_ns_name):
    k8s_ns_list = get_k8s_namespaces()
    for ns in k8s_ns_list:
        metadata = ns["metadata"]
        if k8s_ns_name == metadata["name"]:
            return metadata
    return None


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


def sync_ns_v1():
    region_id = utils.get_region_info("id")
    k8_ns = get_k8s_namespaces()
    for ns in k8_ns:
        req_params = {
            "cluster": {
                "uuid": region_id,
                "name": consts.Configs["region_name"]
            },
            "resource": {
                "name": ns['metadata']['name']
            }
        }
        print "begin sync namespace {} from k8s to alauda metadata".format(ns['metadata']['name'])
        utils.send_request("POST", consts.URLS["create_get_ns"], req_params)


def sync_ns_v2():
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


def sync_ns():
    sqls = ""
    sql_tpl = "insert into resources_resource values(nextval('resources_resource_id_seq'::regclass),'NAMESPACE'," \
              "'{uuid}','{namespace}','{created_by}','2018-06-20 11:50:15','{region_id}:{k8s_ns_name}','{region_id}'," \
              "'','{project_uuid}','');\n"
    if consts.Configs["db_engine"] == "mysql":
        sql_tpl = "insert into resources_resource(`type`,`uuid`,`namespace`,`created_by`,`created_at`,`name`,`region_id`," \
                  "`space_uuid`,`project_uuid`,`namespace_uuid`) values('NAMESPACE','{uuid}','{namespace}','{created_by}'," \
                  "'2018-06-20 11:50:15','{region_id}:{k8s_ns_name}','{region_id}','','{project_uuid}','');\n"

    projects = utils.get_projects()
    for pro in projects:
        name = pro["name"]
        print "begin sync namespace for project {} \n".format(name or "default")
        resource_ns = utils.send_request("GET", consts.URLS["get_resource_ns"], specific_project=name)
        for ns in resource_ns:
            k8s_ns_name = "default--" + ns["name"]
            print "begin build sync sql of namespace for project {} and resource_namespace {}".format(
                name or "default", k8s_ns_name)
            k8s_ns = get_k8s_ns_by_name(k8s_ns_name)
            if k8s_ns:
                sql = sql_tpl.format(uuid=k8s_ns["uid"], namespace=consts.Configs["namespace"],
                                     region_id=utils.get_region_info("id"), created_by=consts.Configs["namespace"],
                                     k8s_ns_name=k8s_ns_name, project_uuid=pro["uuid"])
                sqls += sql
    print sqls


if __name__ == '__main__':
    pass
