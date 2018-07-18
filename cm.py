import os
import json
import services
import consts
import namespaces
from utils import utils


def create_cm():
    current_folder = utils.get_current_folder()
    print "begin create configMap "
    for filename in os.listdir(current_folder):
        if filename.startswith(consts.Prefix["cm_name_prefix"]):
            cm_file = filename
            print "find configMap file " + filename
            if not os.path.exists(current_folder + cm_file):
                raise "configMap file for {} not exists! please check task of init cm".format(current_folder + cm_file)
            cm_data = utils.file_reader(current_folder + cm_file)
            print "config map data for file {},{}".format(filename, json.dumps(cm_data))
            service_name = filename.replace(consts.Prefix["cm_name_prefix"], "")
            svc_detail = services.get_service_detail(service_name)
            data = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "annotations": {},
                    "namespace": svc_detail["space_name"],
                    "name": filename.replace("_", "-")
                },
                "data": cm_data
            }
            print "begin create configMap for {}".format(current_folder + filename)
            res = utils.send_request("POST", consts.URLS["create_cm"], data)
            if isinstance(res, list) and len(res) > 0:
                print "configMap {} create success".format(current_folder + filename)
            else:
                print "configMap {} create ERROR!!!".format(current_folder + filename)
                exit(1)


def get_cm(cm_file):
    return utils.file_reader(cm_file)


def init_cm():
    """
    cm needs to be created
    :return:
    """
    svc_list = services.get_service_list()
    for svc in svc_list:
        svc_detail = services.get_service_detail(svc["uuid"])
        svc_name = svc_detail["service_name"].lower()
        mount_points = svc_detail["mount_points"]
        cm_data = {}
        for mp in mount_points:
            print "init configMap for service {}".format(svc_name)
            cm_name = utils.get_current_folder() + consts.Prefix["cm_name_prefix"] + svc_name

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
            utils.file_writer(cm_name, cm_data)


if __name__ == '__main__':
    pass
