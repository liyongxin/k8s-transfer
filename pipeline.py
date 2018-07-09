import os
import copy
import json
import consts
import namespaces
import services
from utils import utils


def get_all_pipelines_for_current_project(results=None):
    if results is None:
        results = []
    pipeline_list = utils.send_request('GET', consts.URLS['get_all_pipelines'])
    results.extend(pipeline_list['results'])
    # has to be len(svc_list['results']), not svc_list['count']
    if len(pipeline_list['results']) >= 100:
        get_all_pipelines_for_current_project(results)
    return results


def get_pipeline_detail(pl_id):
    pipeline = utils.send_request("GET", consts.URLS["get_or_update_pipeline"].format(pipeline_id=pl_id))
    return pipeline


def init_pipeline():
    all_pips = get_all_pipelines_for_current_project()
    cache_task_types = ["update-service", "exec", "manual-control", ""]
    for pl in all_pips:
        pipeline = get_pipeline_detail(pl["uuid"])
        if "tasks" in pipeline["stages"][0]:
            tasks = pipeline["stages"][0]["tasks"]
            for task in tasks:
                if task["type"] in cache_task_types:
                    cache_pl_file = utils.get_current_folder() + consts.Prefix["pipeline_name_prefix"] + pipeline["name"]
                    utils.file_writer(cache_pl_file, pipeline)


def trans_pipeline(pipeline):
    tasks = pipeline["stages"][0]["tasks"]
    trans_tasks = []
    for task in tasks:
        new_task = trans_common_task(task)
        task_data = task["data"]
        if task["type"] == "update-service":
            # update from old k8s service to new k8s app svc
            new_task["type"] = "update-service-new"
            transed_data = trans_update_service_task(task_data)
            new_task["data"] = transed_data
            trans_tasks.append(new_task)
        elif task["type"] == "exec":
            transed_data = trans_exec_task(task_data)
            new_task["data"] = transed_data
            trans_tasks.append(new_task)
        elif task["type"] == "manual-control" and "exec_enabled" in task_data and task_data["exec_enabled"]:
            transed_data = trans_manual_control_task(task_data)
            new_task["data"] = transed_data
            trans_tasks.append(new_task)
        elif task["type"] == "test-container":
            task_data["space_name"] = pipeline["space_name"]
            transed_data = trans_test_container_task(task_data)
            new_task["data"] = transed_data
            trans_tasks.append(new_task)
        else:
            # todo , confirm should trans common data for other types
            trans_tasks.append(task)
    pipeline["stages"][0]["tasks"] = trans_tasks
    return pipeline


def trans_common_task(task):
    common_task = {
        "order": task["order"],
        "name": task["name"],
        "type": task["type"],
        "region_uuid": task["region_uuid"],
        "region": consts.Configs["region_name"],
        "timeout": task["timeout"],
    }
    return common_task


def trans_manual_control_task(task_data):
    transed_data = copy.deepcopy(task_data)
    link = task_data["link"]
    service_name = link["name"]
    new_svc_res = services.get_new_svc_by_name(service_name)
    if len(new_svc_res) == 0:
        print "ERROR: find no svc for pipeline update ,will skip"
        return task_data
    new_svc = new_svc_res[0]
    transed_data["link"] = {
        "name": service_name,
        "type": "application-service",
        "uuid": new_svc["resource"]["uuid"],
        "parent": new_svc["parent"]["name"],
        "parent_uuid": new_svc["parent"]["uuid"],
        "namespace": new_svc["namespace"]["name"],
        "perm_service": "update"
    }

    return transed_data


def trans_test_container_task(task_data):
    transed_data = copy.deepcopy(task_data)
    k8s_namespace_name = "default--" + transed_data["space_name"]
    k8s_namespace_resource = namespaces.get_alauda_ns_by_name(k8s_namespace_name)
    transed_data["k8s_namespace_uuid"] = k8s_namespace_resource["uuid"]
    transed_data["k8s_namespace"] = k8s_namespace_name
    if "link" in transed_data:
        del transed_data["link"]
    env_params = {
        "env_vars": transed_data["env_vars"]
    }
    if "env_file_uuid" in transed_data and "env_file" in transed_data:
        env_params["env_files"] = [{
            "name": transed_data["env_file_uuid"],
            "uuid": transed_data["env_file"]
        }]
    transed_data["env"] = get_svc_env(env_params)
    return transed_data


def trans_exec_task(task_data):
    transed_data = copy.deepcopy(task_data)
    link = transed_data["link"]
    service_name = link["name"].lower()
    new_svc_res = services.get_new_svc_by_name(service_name)
    if len(new_svc_res) == 0:
        print "ERROR: find no svc for pipeline update ,will skip"
        return task_data
    new_svc = new_svc_res[0]
    transed_data["link"] = {
        "name": service_name,
        "type": "application-service",
        "uuid": new_svc["resource"]["uuid"],
        "parent": new_svc["parent"]["name"],
        "parent_uuid": new_svc["parent"]["uuid"],
        "perm_service": "update",
        "namespace": new_svc["namespace"]["name"]
    }
    # transed_data = {

    #    "entrypoint": task_data["entrypoint"],
    #    "command": task_data["command"]
    # }
    # manual control exec , trans instance
    if "instance" in transed_data:
        svc_instances = services.get_service_v2_instances(new_svc["resource"]["uuid"])
        transed_data["instance"] = svc_instances[0]["metadata"]["name"],
        container_name = service_name + "-0"
        transed_data["containers"] = [
            container_name
        ]
    print "\ntrans_exec_task data is {}\n".format(json.dumps(transed_data))
    return transed_data


def get_svc_env(task_data):
    result = []
    if "env_vars" in task_data:
        for key in task_data["env_vars"]:
            result.append({
                "name": key,
                "value": task_data["env_vars"][key]
            })
    if "env_files" in task_data:
        for envfile in task_data["env_files"]:
            envfile_detail = services.get_envfile_by_id(envfile["uuid"])
            for env in envfile_detail["content"]:
                result.append({
                    "name": env[0],
                    "value": env[1]
                })
    return result


def trans_update_service_task(task_data):
    transed_data = copy.deepcopy(task_data)
    service = task_data["service"]
    service_name = service["name"].lower()
    new_svc_res = services.get_new_svc_by_name(service_name)
    if len(new_svc_res) == 0:
        print "ERROR: find no svc for pipeline update ,will skip"
        return task_data
    new_svc = new_svc_res[0]
    transed_data["env_files"] = []
    transed_data["mount_points"] = []
    transed_data["env_vars"] = {}
    transed_data["automatic_rollback"] = True

    transed_data["service"] = {
        "name": service_name,
        "is_new": True,
        "type": "application-service",
        "uuid": new_svc["resource"]["uuid"],
        "parent": new_svc["parent"]["name"],
        "parent_uuid": new_svc["parent"]["uuid"],
        "namespace": new_svc["namespace"]["name"],
        # "triggerImage": service["triggerImage"],
        "containers": [
            {
                "name": service_name + "-0",
                "use_image_in_trigger": True,
                "env": get_svc_env(task_data)
            }
        ]
    }

    return transed_data


def update_pipeline(pipeline):
    utils.send_request("PUT", consts.URLS["get_or_update_pipeline"].format(pipeline_id=pipeline["uuid"]), pipeline)


def handle_pipeline():
    print "\nbegin update pipeline data\n"
    current_folder = utils.get_current_folder()
    for filename in os.listdir(current_folder):
        if filename.startswith(consts.Prefix["pipeline_name_prefix"]):
            pipeline_file = filename
            if utils.no_task_record(pipeline_file):
                print "\nfind pipeline file " + filename
                if not os.path.exists(current_folder + pipeline_file):
                    raise "pipeline file for {} not exists! please check task of init lb".format(pipeline_file)
                pipeline_data = utils.file_reader(current_folder + pipeline_file)
                pipeline_name = pipeline_data["name"]
                print "\nbegin handle pipeline {} \n".format(pipeline_name)
                transed_pipeline = trans_pipeline(pipeline_data)
                print "transed pipeline data is {}".format(json.dumps(transed_pipeline))
                print "\n begin update pipeline {}".format(transed_pipeline["name"])
                update_pipeline(transed_pipeline)
                utils.task_record(pipeline_file)


def main():
    if utils.no_task_record("init_pipeline"):
        init_pipeline()
        utils.task_record("init_pipeline")
    if utils.no_task_record("trans_pipeline"):
        handle_pipeline()
        utils.task_record("trans_pipeline")


if __name__ == '__main__':
    pass
