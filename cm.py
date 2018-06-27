import os
import json
import services
import consts
import namespaces
from utils import utils


def create_cm_v1():
    svc_list = services.get_service_list()
    for svc in svc_list:
        cm_file_name = consts.Prefix["cm_name_prefix"] + svc["service_name"]
        if not os.path.exists(cm_file_name):
            print "ERROR:cm file {} doesn't exists!".format(cm_file_name)
            continue
        reader = open(cm_file_name, "r")
        cm_data = json.load(reader)
        print "config map data for file {}".format(cm_file_name)
        print cm_data
        data = {
            "resource": {
                "name": cm_file_name
            },
            "namespace": {
                "uuid": namespaces.get_alauda_ns_by_name(svc["service_namespace"])["uuid"],
                "name": svc["service_namespace"],
            },
            "cluster": {
                "name": svc["region_name"],
                "uuid": svc["region_uuid"]
            },
            "kubernetes": {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": cm_file_name
                },
                "data": cm_data
            }
        }


def create_cm():
    current_folder = utils.get_current_folder()
    print "begin create configMap "
    for filename in os.listdir(current_folder):
        if filename.startswith(consts.Prefix["cm_name_prefix"]):
            cm_file = filename
            print "find configMap file " + filename
            if not os.path.exists(current_folder + cm_file):
                raise "configMap file for {} not exists! please check task of init cm".format(current_folder + cm_file)
            reader = open(current_folder + cm_file, "r")
            cm_data = json.load(reader)
            print "config map data for file {},{}".format(filename, json.dumps(cm_data))
            service_name = filename.replace(consts.Prefix["cm_name_prefix"], "")
            svc_detail = services.get_service_detail(service_name)
            data = {
                "resource": {
                    "name": filename.replace("_", "-")
                },
                "namespace": {
                    "uuid": namespaces.get_alauda_ns_by_name(svc_detail["service_namespace"])["uuid"],
                    "name": svc_detail["service_namespace"],
                },
                "cluster": {
                    "name": svc_detail["region_name"],
                    "uuid": svc_detail["region_uuid"]
                },
                "kubernetes": {
                    "apiVersion": "v1",
                    "kind": "ConfigMap",
                    "metadata": {
                        "name": filename.replace("_", "-")
                    },
                    "data": cm_data
                }
            }
            print "begin create configMap for {}".format(current_folder + filename)
            utils.send_request("POST", consts.URLS["create_cm"], data)


def get_cm(cm_file):
    reader = open(cm_file, "r")
    cm_data = json.load(reader)
    reader.close()
    return cm_data


def init_cm():
    """
    cm needs to be created
    :return:
    """
    svc_list = services.get_service_list()
    for svc in svc_list:
        svc_detail = services.get_service_detail(svc["uuid"])
        svc_name = svc_detail["service_name"]
        mount_points = svc_detail["mount_points"]
        cm_data = {}
        for mp in mount_points:
            print "init configMap for service {}".format(svc_name)
            cm_name = utils.get_current_folder() + consts.Prefix["cm_name_prefix"] + svc_name
            writer = open(cm_name, "w")

            if mp["type"] == "config":
                value = mp["value"]
                key = value["key"]
                conf_file_name = value["name"]
                data = utils.send_request("GET", consts.URLS["get_config_content"].format(filename=conf_file_name))
                print "config file {} response is ".format(conf_file_name)
                print data
                if "content" in data:
                    for item in data["content"]:
                        if item["key"] == key:
                            content = item["value"]
                            cm_data[key] = content
            elif mp["type"] == "raw" or mp["type"] == "text":
                key = "key" + mp["path"].replace("/", "-")
                content = mp["value"]
                cm_data[key] = content
            else:
                raise "Unknown config type " + mp["type"]
            writer.write(json.dumps(cm_data))
            writer.close()


if __name__ == '__main__':
    pass
