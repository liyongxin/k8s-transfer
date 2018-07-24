import os
import json
import services
import consts
import applications
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
            is_app = False
            if filename.startswith(consts.Prefix["cm_name_prefix"] + consts.Prefix["app_cm_flag_file"]):
                is_app = True
            filename_pre = consts.Prefix["cm_name_prefix"] + consts.Prefix["app_cm_flag_file"] if is_app\
                else consts.Prefix["cm_name_prefix"]
            service_uuid = filename.replace(filename_pre, "")
            print "find cm service uuid {}, type is {}".format(service_uuid, "app" if is_app else "service")
            svc_detail = applications.get_app_service_detail(service_uuid) if is_app \
                else services.get_service_detail(service_uuid)
            data = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "annotations": {},
                    "namespace": applications.get_app_svc_namespace(svc_detail) if is_app else svc_detail["space_name"],
                    "name": filename.replace("_", "-")
                },
                "data": cm_data
            }
            print "begin create configMap for {}".format(current_folder + filename)
            res = utils.send_request("POST", consts.URLS["create_cm"], data)
            if isinstance(res, list) and len(res) > 0:
                print "configMap {} create success,list".format(current_folder + filename)
            elif isinstance(res, dict) and "result" in res and len(res["result"]) > 0:
                print "create namespace for {} success".format(current_folder + filename)
            elif isinstance(res, dict) and "errors" in res and \
                            res["errors"][0]["message"].find("already exists") >= 0:
                print res["errors"][0]["message"] + ", will be skipped"
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
        uuid = svc["uuid"]
        svc_detail = services.get_service_detail(uuid)
        init_cm_handler(svc_detail)


def init_cm_handler(svc_detail):
    svc_name = svc_detail["service_name"].lower()
    svc_uuid = svc_detail["uuid"]
    mount_points = svc_detail["mount_points"]
    cm_data = {}
    cm_name_pre = utils.get_current_folder() + consts.Prefix["cm_name_prefix"]
    if svc_detail["app_name"]:
        cm_name_pre = cm_name_pre + consts.Prefix["app_cm_flag_file"]
    for mp in mount_points:
        print "init configMap for service {}".format(svc_name)
        cm_name = cm_name_pre + svc_uuid

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


def init_app_cm():
    """
    cm needs to be created
    :return:
    """
    app_list = applications.get_app_list()
    for app in app_list:
        for app_service in app["services"]:
            svc_detail = applications.get_app_service_detail(app_service["uuid"])
            init_cm_handler(svc_detail)


if __name__ == '__main__':
    pass
