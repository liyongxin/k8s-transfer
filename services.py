import json
import time
import consts
import namespaces
import project
import lb
from os import path
from utils import utils


def get_svc_list_for_current_project(results=None):
    if results is None:
        results = []
    svc_list = utils.send_request('GET', consts.URLS['get_svc_list'])
    results.extend(svc_list['results'])
    # has to be len(svc_list['results']), not svc_list['count']
    if len(svc_list['results']) >= 100:
        get_svc_list_for_current_project(results)
    return results


def init_svc_list():
    svc_list = get_svc_list_for_current_project(results=[])
    file_name = utils.get_current_folder() + consts.Prefix["service_list_file"]
    writer = open(file_name, "w")
    writer.write(json.dumps(svc_list))
    writer.close()


def init_svc_detail():
    svc_list = get_service_list()
    for svc in svc_list:
        file_name_id = utils.get_current_folder() + consts.Prefix["service_detail_file"] + svc["uuid"]
        file_name_svc_name = utils.get_current_folder() + consts.Prefix["service_detail_file"] + svc["service_name"]
        svc_detail = utils.send_request("GET", consts.URLS["get_or_delete_svc_detail"].format(service_id=svc["uuid"]))
        writer_id = open(file_name_id, "w")
        writer_id.write(json.dumps(svc_detail))
        writer_id.close()

        # detail for svc_name
        writer_name = open(file_name_svc_name, "w")
        writer_name.write(json.dumps(svc_detail))
        writer_name.close()


def get_service_detail(svc_id_or_name):
    svc_detail = {}
    file_name = utils.get_current_folder() + consts.Prefix["service_detail_file"] + svc_id_or_name
    if path.exists(file_name):
        reader = open(file_name, "r")
        svc_detail = json.load(reader)
        reader.close()
    else:
        raise Exception("service detail file {} doesn't exists!".format(file_name))
    return svc_detail


def get_service_list():
    results = []
    file_name = utils.get_current_folder() + consts.Prefix["service_list_file"]
    if path.exists(file_name):
        reader = open(file_name, "r")
        results = json.load(reader)
        reader.close()
    else:
        raise Exception("services file doesn't exists!")
    return results


def get_new_svc_by_name(svc_name):
    url = consts.URLS["get_svc_v2"].format(service_name=svc_name)
    project_name = project.get_project_by_svc_name(svc_name)
    print "find svc {} was in project {}".format(svc_name, project_name)
    data = utils.send_request('GET', url, specific_project=project_name)
    if data["count"] != 1:
        print "Attention!!! not found new svc named {}".format(svc_name)
    #    raise Exception("find {count} instances for {svc_name} ".format(count=data["count"], svc_name=svc_name))
    return data["results"]


def get_svc_labels(svc_id):
    svc_detail = get_service_detail(svc_id)
    lables = {
        "service.alauda.io/name": svc_detail["service_name"],
    }
    for lable in svc_detail["labels"]:
        lables[lable["key"]] = lable["value"]
    return lables


def get_svc_affinity(svc):

    pod_affinity = svc["kube_config"]["pod"]["podAffinity"]
    if "requiredDuringSchedulingIgnoredDuringExecution" in pod_affinity:
        for item in pod_affinity["requiredDuringSchedulingIgnoredDuringExecution"]:
            if "labelSelector" in item:
                match_expressions = item["labelSelector"]
                for expression in match_expressions["matchExpressions"]:
                    if "key" in expression and expression["key"] == "alauda_service_id":
                        expression["key"] = "service.alauda.io/name"
                    if "values" in expression:
                        tmp = []
                        for value in expression["values"]:
                            tmp.append(get_service_detail(value)["service_name"])
                        expression["values"] = tmp

    pod_antiAffinity = svc["kube_config"]["pod"]["podAntiAffinity"]
    if "requiredDuringSchedulingIgnoredDuringExecution" in pod_antiAffinity:
        for item in pod_antiAffinity["requiredDuringSchedulingIgnoredDuringExecution"]:
            if "labelSelector" in item:
                match_expressions = item["labelSelector"]
                for expression in match_expressions["matchExpressions"]:
                    if "key" in expression and expression["key"] == "alauda_service_id":
                        expression["key"] = "service.alauda.io/name"
                    if "values" in expression:
                        tmp = []
                        for value in expression["values"]:
                            tmp.append(get_service_detail(value)["service_name"])
                        expression["values"] = tmp

    return {
        "podAffinity": pod_affinity,
        "podAntiAffinity": pod_antiAffinity
    }


def get_svc_env(svc_id):
    svc_detail = get_service_detail(svc_id)
    result = []
    env_obj = {}
    if "instance_envvars" in svc_detail:
        for key in svc_detail["instance_envvars"]:
            result.append({
                "name": key,
                "value": svc_detail["instance_envvars"][key]
            })
    if "envfiles" in svc_detail:
        for envfile in svc_detail["envfiles"]:
            content = envfile["content"]
            for env in content:
                result.append({
                    "name": env[0],
                    "value": env[1]
                })
    return result


def get_envfile_by_id(file_id):
    return utils.send_request("GET", consts.URLS["get_envfile"])


def get_health_check(svc_id):
    svc_detail = get_service_detail(svc_id)
    hc = svc_detail["health_checks"][0]
    result = {
        "initialDelaySeconds": hc["grace_period_seconds"],
        "periodSeconds": hc["interval_seconds"],
        "timeoutSeconds": hc["timeout_seconds"],
        "successThreshold": 1,
        "failureThreshold": hc["max_consecutive_failures"],
        "httpGet": {
            "path": hc["path"],
            "scheme": hc["protocol"],
            "port": hc["port"]
        }
    }
    return result


def get_create_method(svc_id):
    svc = get_service_detail(svc_id)
    if len(svc["mount_points"]) > 0:
        return "yaml"
    else:
        return "UI"


def get_volume_mounts(svc_id):
    svc = get_service_detail(svc_id)
    mount_points = svc["mount_points"]
    svc_name = svc["service_name"]
    volume_mounts = []
    volumes = []
    index = 0
    for mp in mount_points:
        if mp["type"] == "config":
            value = mp["value"]
            config_key = value["key"]
            k8_cm_name = consts.Prefix["cm_name_prefix"] + svc_name
            volume_obj = {
                "name": "configmap-" + svc_name + "-" + str(index),
                "configMap": {
                    "name": k8_cm_name,
                    "items": [{
                        "key": config_key,
                        "path": config_key
                    }]
                }
            }

            mount_obj = {
                "mountPath": mp["path"],
                "name": "configmap-" + svc_name + "-" + str(index),
                "subPath": config_key
            }
            volumes.append(volume_obj)
            volume_mounts.append(mount_obj)
        elif mp["type"] == "raw" or mp["type"] == "text":
            k8_cm_name = consts.Prefix["cm_name_prefix"] + svc_name
            raw_key = "key" + mp["path"].replace("/", "-")
            volume_obj = {
                "name": "configmap-" + svc_name + "-" + str(index),
                "configMap": {
                    "name": k8_cm_name,
                    "items": [{
                        "key": raw_key,
                        "path": raw_key
                    }]
                }
            }
            mount_obj = {
                "mountPath": mp["path"],
                "name": "configmap-" + svc_name + "-" + str(index),
                "subPath": raw_key
            }
            volumes.append(volume_obj)
            volume_mounts.append(mount_obj)
        else:
            raise "Unknown config type " + mp["type"]
        index += 1
    # handle host_path, gfs, not include  ebs
    if "volumes" in svc:
        for vol in svc["volumes"]:
            driver_name = vol["driver_name"]
            if driver_name == "":   # host path
                volume_obj = {
                    "name": "hostpath-" + svc_name + "-" + str(index),
                    "hostPath": {
                        "path": vol["volume_name"]
                    }
                }
                mount_obj = {
                    "mountPath": vol["app_volume_dir"],
                    "name": "hostpath-" + svc_name + "-" + str(index)
                }
                volumes.append(volume_obj)
                volume_mounts.append(mount_obj)
            if driver_name == "glusterfs":  # glusterfs
                volume_obj = {
                    "name": "glusterfs-" + svc_name + "-" + str(index),
                    "glusterfs": {
                        "endpoints": "glusterfs-endpoints",
                        "path": vol["volume_name"]
                    }
                }
                mount_obj = {
                    "mountPath": vol["app_volume_dir"],
                    "name": "glusterfs-" + svc_name + "-" + str(index)
                }
                volumes.append(volume_obj)
                volume_mounts.append(mount_obj)
            index += 1
    print "volumes, volume_mounts foo svc {}".format(svc_name)
    print {
        "mounts": volume_mounts,
        "volumes": volumes
    }
    return {
        "mounts": volume_mounts,
        "volumes": volumes
    }


def get_host_network(svc):
    if svc["network_mode"] == "HOST":
        return True
    else:
        return False


def get_node_selector(svc):
    if "node_selector" in svc:
        return svc["node_selector"]
    else:
        return {}


def get_svc_cluster_ports(svc_ports):
    ports = []
    index = 0
    for port in svc_ports:
        port_obj = {
            "name": "tcp-" + str(index),
            "protocol": "TCP",
            "port": port,
            "targetPort": port
        }
        index += 1
        ports.append(port_obj)
    return ports


def get_svc_node_ports(svc_ports):
    ports = []
    index = 0
    for port in svc_ports:
        port_obj = {
            "name": "np-" + str(index),
            "protocol": "TCP",
            "port": port,
            "targetPort": port
        }
        index += 1
        ports.append(port_obj)
    return ports


def get_subnet_by_id(subnet_id):
    subnets = utils.send_request("GET", consts.URLS["get_subnets"])
    for subnet in subnets:
        if subnet_id == subnet["subnet_id"]:
            return subnet["subnet_name"]
    return None


def get_service_v2_instances(service_id):
    instances = utils.send_request("GET", consts.URLS["get_svc_v2_instances"].format(service_id=service_id))
    return instances


def get_instance_ips(instances):
    ips = []
    for instance in instances:
        if instance["container_ip"]:
            ips.append(instance["container_ip"])
        else:
            raise Exception("find no container ip for macvlan svc !! break!!")
    return ",".join(ips)


def trans_pod_controller(svc):
    kubernetes_attr = []
    service_name = svc["service_name"]
    k8s_controller = {
        "apiVersion": "extensions/v1beta1",
        "kind": svc["pod_controller"],
        "metadata": {
            "namespace": "",
            "name": service_name
        },
        "spec": {
            "template": {
                "metadata": {
                    "labels": get_svc_labels(svc["uuid"])
                },
                "spec": {
                    "affinity": get_svc_affinity(svc),
                    "containers": [
                        {
                            "name": service_name + "-0",
                            "image": svc["image_name"] + ":" + svc["image_tag"],
                            "imagePullPolicy": "Always",
                            "resources": {
                                "requests": {
                                    "memory": str(svc["custom_instance_size"]["mem"]) + "M",
                                    "cpu": svc["custom_instance_size"]["cpu"]
                                },
                                "limits": {
                                    "memory": str(svc["custom_instance_size"]["mem"]) + "M",
                                    "cpu": svc["custom_instance_size"]["cpu"]
                                }
                            },
                            "env": get_svc_env(svc["uuid"]),
                            # "livenessProbe": get_health_check(svc["uuid"]),
                            "volumeMounts": get_volume_mounts(svc["uuid"])["mounts"]
                        }
                    ],
                    "hostNetwork": get_host_network(svc),
                    "nodeSelector": get_node_selector(svc),
                    "volumes": get_volume_mounts(svc["uuid"])["volumes"]
                }
            },
            "replicas": svc["target_num_instances"],
            "strategy": {
                "type": "RollingUpdate",
                "rollingUpdate": {
                    "maxSurge": svc["update_strategy"]["max_surge"],
                    "maxUnavailable": svc["update_strategy"]["max_unavailable"]
                }
            }
        }
    }
    # handle macvlan annotations, subnet_id
    # todo
    if svc["network_mode"] == "MACVLAN" and svc["subnet_id"]:
        print "\nbegin handle macvlan subnet"
        subnet_name = get_subnet_by_id(svc["subnet_id"])
        print "get subnet name {} for subnet_id {}".format(subnet_name, svc["subnet_id"])
        k8s_controller["spec"]["template"]["metadata"]["annotations"] = {
                "subnet.alauda.io/name": subnet_name,
                "subnet.alauda.io/ipAddrs": get_instance_ips(svc["instances"])  # "192.168.10.100,192.168.10.111"
            }

    # handle self command
    if svc["entrypoint"] and svc["run_command"]:
        k8s_controller["spec"]["template"]["spec"]["containers"][0]["args"] = [
            svc["run_command"]
        ]
        k8s_controller["spec"]["template"]["spec"]["containers"][0]["command"] = [
            svc["entrypoint"]
        ]
    if "health_checks" in svc and len(svc["health_checks"]) > 0:
        k8s_controller["spec"]["template"]["spec"]["containers"][0]["livenessProbe"] = get_health_check(svc["uuid"])

    kubernetes_attr.append(k8s_controller)

    # handle "autoscaling/v1"
    autoscaling = {
        "apiVersion": "autoscaling/v1",
        "kind": "HorizontalPodAutoscaler",
        "metadata": {
            "name": service_name,
            "namespace": ""
        },
        "spec": {
            "maxReplicas": 1,
            "minReplicas": 1,
            "scaleTargetRef": {
                "apiVersion": "extensions/v1beta1",
                "kind": "Deployment",
                "name": service_name
            }
        }
    }
    kubernetes_attr.append(autoscaling)
    # handle clusterIp
    if "ports" in svc and len(svc["ports"]) > 0:
        k8s_service = {
            "kind": "Service",
            "apiVersion": "v1",
            "metadata": {
                "name": service_name,
                "namespace": svc["service_namespace"]
            },
            "spec": {
                "selector": {
                    "service.alauda.io/name": service_name
                },
                "ports": get_svc_cluster_ports(svc["ports"])
            }
        }
        kubernetes_attr.append(k8s_service)

    # handle nodeport
    if "kube_config" in svc and "services" in svc["kube_config"] and len(svc["kube_config"]["services"]) > 0:
        for kube_svc in svc["kube_config"]["services"]:
            if kube_svc["type"] == "NodePort":
                k8s_service = {
                    "kind": "Service",
                    "apiVersion": "v1",
                    "metadata": {
                        "name": kube_svc["name"],
                        "namespace": svc["service_namespace"]
                    },
                    "spec": {
                        "selector": {
                            "service.alauda.io/name": svc["service_name"]
                        },
                        # old svc one service item can only add one nodeport
                        "ports": [{
                            "name": "np-" + str(kube_svc["node_port"]),
                            "nodePort": kube_svc["node_port"],
                            "port": kube_svc["container_port"],
                            "protocol": "TCP",
                            "targetPort": kube_svc["container_port"]
                        }],
                        "type": "NodePort"
                    }
                }
                kubernetes_attr.append(k8s_service)
    return kubernetes_attr


def trans_svc_data(svc):
    app_data = {
        "resource": {
            "create_method": get_create_method(svc["uuid"])
        },
        "kubernetes": []
    }
    if svc["app_name"]:
        app_data["resource"]["name"] = svc["app_name"]
    else:
        app_data["resource"]["name"] = consts.Prefix["app_name_prefix"] + svc["service_name"]

    app_data["namespace"] = {
        "name": svc["service_namespace"],
        "uuid": namespaces.get_alauda_ns_by_name(svc["service_namespace"])["uuid"]
    }
    app_data["cluster"] = {
        "name": svc["region_name"],
        "uuid": svc["region_uuid"]
    }

    app_data["kubernetes"] = trans_pod_controller(get_service_detail(svc["uuid"]))
    return app_data


def create_app(data):
    url = consts.URLS["create_app"]
    return utils.send_request("POST", url, data)


def delete_old_svc(svc_id):
    utils.send_request("DELETE", consts.URLS["get_or_delete_svc_detail"].format(service_id=svc_id))


def get_v1_svc_by_api(svc_id):
    return utils.send_request("GET", consts.URLS["get_or_delete_svc_detail"].format(service_id=svc_id))


def get_app_by_api(app_id):
    return utils.send_request("GET", consts.URLS["get_app_by_id"].format(service_id=app_id))


def update_app(app):
    data = {
        "namespace": app["cluster"]["name"],
        "kubernetes": app["kubernetes"]
    }
    utils.send_request("PATCH", consts.URLS["get_app_by_id"].format(service_id=app["resource"]["uuid"]), data)


def main():
    svc_list = get_service_list()
    for svc in svc_list:
        service_name = svc["service_name"]
        service_status = svc["current_status"]

        task_single_svc = "trans_svc_{svc_id}_{svc_name}".format(svc_id=svc["uuid"], svc_name=service_name)
        if utils.no_task_record(task_single_svc):
            # skipped excluded services in consts.ExcludedServiceNames
            if service_name in consts.ExcludedServices:
                print "skipped service {} because configed in consts.ExcludedServiceNames".format(service_name)
                continue
            if service_status not in consts.IncludeServiceStatus:
                raw_tips = "{service_name} status is {service_status}, input Yes/No for continue or skip ".\
                    format(service_name=service_name, service_status=service_name)
                answer = raw_input(raw_tips)
                if answer.lower() == "no":
                    print "skipped service {} because current_status is {}".format(service_name, service_status)
                    continue
            print "begin trans service data to app data for service {}".format(service_name)
            app_data = trans_svc_data(svc)
            print "app data for service {}".format(service_name)
            print app_data
            print "\nbegin delete service old service {}".format(service_name)
            delete_old_svc(svc["uuid"])
            print "\nwaiting service {} for delete ".format(service_name)
            for count in range(20):
                time.sleep(3)
                svc = get_v1_svc_by_api(svc["uuid"])
                if not svc:
                    print "\n service {} delete done".format(service_name)
                    break

            print "\nbegin create app for service {} ".format(service_name)
            app_info = create_app(app_data)
            # print app_info
            print "\nwaiting new app {} for create ".format(service_name)
            for count in range(20):
                time.sleep(3)
                app = get_app_by_api(app_info["resource"]["uuid"])
                app_current_state = app["resource"]["status"]
                if app_current_state == "Running":
                    print "\n app {} create done".format(service_name)
                    break
                else:
                    print "\n app {} current status is {}, continue waiting...".format(service_name, app_current_state)
            # begin update app for bind old tag
            app = get_app_by_api(app_info["resource"]["uuid"])
            update_app(app)
            print "\nwaiting app {} for update ".format(service_name)
            for count in range(20):
                time.sleep(3)
                app = get_app_by_api(app_info["resource"]["uuid"])
                app_current_state = app["resource"]["status"]
                if app_current_state == "Running":
                    print "\n app {} update done".format(service_name)
                    break
                else:
                    print "\n app {} current status is {}, continue waiting...".format(service_name, app_current_state)
            # handle lb binding
            lb.handle_lb_for_svc(service_name)
            # if service_status == "Stopped":
            #    app_id = app_info["resource"]["uuid"]
            #    utils.send_request("PUT", consts.URLS["stop_app"].format(app_id=app_id))
            utils.task_record(task_single_svc)
            print "!!!!!Status Confirm: old service status is {}, " \
                  "please check if should change by hands".format(service_status)
            exit(1)


if __name__ == '__main__':
    pass
