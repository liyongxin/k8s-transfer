import os
import json
import copy
import consts
import services
from utils import utils


def init_lb_list():
    lb_list = utils.send_request("GET", consts.URLS["get_lb"])
    for lb in lb_list:
        # lb_ft = get_lb_frontends(lb["name"])
        filename = utils.get_current_folder() + consts.Prefix["lb_name_prefix"] + lb["name"]
        utils.file_writer(filename, lb)


def init_svc_lb():
    svc_list = services.get_service_list()
    get_lb_url = consts.URLS["get_lb"]
    for svc in svc_list:
        url = get_lb_url + "&service_id=" + svc["uuid"]
        svc_lb_data = utils.send_request("GET", url)
        filename = utils.get_current_folder() + consts.Prefix["lb_name_prefix"] + svc["service_name"]
        utils.file_writer(filename, svc_lb_data)


def get_lb(lb_file):
    return utils.file_reader(utils.get_current_folder() + lb_file)


def get_svc_lb(svc_name):
    return utils.file_reader(utils.get_current_folder() + consts.Prefix["lb_name_prefix"] + svc_name)


def get_lb_frontends(lb_name):
    url = consts.URLS["lb_frontends"].format(lb_name=lb_name)
    lb_ft = utils.send_request("GET", url)
    print "lb frontends for {}".format(lb_name)
    print lb_ft
    return lb_ft


def create_frontend(lb_name, frontend):
    protocol = frontend["protocol"]
    data = {
        "certificate_id": frontend["certificate_id"],
        "certificate_name": frontend["certificate_name"],
        "container_port": frontend["container_port"],
        "port": frontend["port"],
        "service_id": "",
        "protocol": frontend["protocol"],
        "container_ports": []
        # "space_id": frontend["space_id"],
        # "space_name": frontend["space_name"]
    }
    if frontend["service_id"] and frontend["service_name"]:
        new_svcs = services.get_new_svc_by_name(frontend["service_name"])
        data["service_id"] = new_svcs[0]["resource"]["uuid"]

    utils.send_request("POST", consts.URLS["lb_frontends"].format(lb_name=lb_name), data)


def create_rule(lb_name, frontend_port, rule):
    unused_keys = ["priority", "services", "type", "rule_id"]
    for key in unused_keys:
        if key in rule:
            del rule[key]
    return utils.send_request("POST", consts.URLS["lb_create_rule"].format(lb_name_or_id=lb_name, port=frontend_port), rule)


def bind_rule_svc(lb_name, port, rule_id, service_list):
    url = consts.URLS["lb_bind_svc_rule"].format(lb_name_or_id=lb_name, port=port, rule_id=rule_id)
    data = []
    for service in service_list:
        if service["service_id"] and service["service_name"]:
            service_name = service["service_name"]
            new_services = services.get_new_svc_by_name(service_name)
            if len(new_services) == 0:
                print "find new service failed because no service named {}, will skipped for lb {} and port {}".format(service_name, lb_name, port)
                continue
            print "find new service for {}, {}".format(service_name, json.dumps(new_services))
            data.append({
                "service_id": new_services[0]["resource"]["uuid"],
                "container_ports": [
                    service["container_port"]
                ],
                "container_port": service["container_port"],
                "weight": service["weight"]
            })
        else:
            print "find service with no id and name when bind for lb {} and port {},will be skipped".format(lb_name, port)

    print "begin bind new service for {} and port {} and rule {}, service_list is {}".format(lb_name, port, rule_id, json.dumps(service_list))
    utils.send_request("POST", url, data)


def main():
    print "\nbegin handle lb bindings\n"
    current_folder = utils.get_current_folder()
    for filename in os.listdir(current_folder):
        if filename.startswith(consts.Prefix["lb_name_prefix"]):
            lb_file = filename
            print "\nfind lb file " + filename
            if not os.path.exists(current_folder + lb_file):
                raise "lb file for {} not exists! please check task of init lb".format(lb_file)
            lb_datas = get_lb(lb_file)
            lb_name = lb_datas["name"]
            print "\nbegin handle lb {} \n".format(lb_name)
            for frontend in lb_datas["frontends"]:
                port = frontend["port"]
                if utils.no_task_record(lb_file + "_frontend_" + str(port)):
                    print "begin create frontend for  lb {} and port {}".format(lb_name, port)
                    create_frontend(lb_name, frontend)
                    utils.task_record(lb_file + "_frontend_" + str(port))

                if frontend["protocol"] == "tcp":
                    print "\nskip tcp frontend {} rules create\n".format(port)
                    continue
                rules = frontend["rules"]
                for rule in rules:
                    if utils.no_task_record(lb_file + "_frontend_" + str(port) + "_rule_" + rule["rule_id"]):
                        if rule["type"] == "system":
                            continue
                        print "\nbegin create rule for domain {} and port {}".format(rule["domain"], port)
                        rule_info = create_rule(lb_name, port, copy.deepcopy(rule))
                        # record rule create task
                        utils.task_record(lb_file + "_frontend_" + str(port) + "_rule_" + rule["rule_id"])

                        print "\nnew rule info is: {}\n".format(json.dumps(rule_info))
                        if "services" in rule and len(rule["services"]) > 0:
                            bind_rule_svc(lb_name, frontend["port"], rule_info["data"]["rule_id"], rule["services"])


def handle_lb_for_svc(svc_name):
    print "\nbegin handle lb bindings for svc {}".format(svc_name)
    svc_lb_data = get_svc_lb(svc_name)
    for lb_data in svc_lb_data:
        lb_name = lb_data["name"]
        for frontend in lb_data["frontends"]:
            port = frontend["port"]
            frontend_task = lb_name + "_frontend_" + str(port)
            if utils.no_task_record(frontend_task):
                print "begin create frontend for  lb {} and port {}".format(lb_name, port)
                create_frontend(lb_name, frontend)
                utils.task_record(frontend_task)
            if frontend["protocol"] == "tcp":
                print "\nskip tcp frontend {} rules create\n".format(port)
                continue
            rules = frontend["rules"]
            for rule in rules:
                rule_task = lb_name + "_frontend_" + str(port) + "_rule_" + rule["rule_id"]
                if utils.no_task_record(rule_task):
                    if rule["type"] == "system":
                        continue
                    print "\nbegin create rule for domain {} and port {}".format(rule["domain"], port)
                    rule_info = create_rule(lb_name, port, copy.deepcopy(rule))
                    # record rule create task
                    utils.task_record(rule_task)

                    print "\nnew rule info is: {}\n".format(json.dumps(rule_info))
                    if "services" in rule and len(rule["services"]) > 0:
                        bind_rule_svc(lb_name, frontend["port"], rule_info["data"]["rule_id"], rule["services"])


if __name__ == '__main__':
    pass
