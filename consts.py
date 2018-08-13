
Configs = {
    "api_url": "http://140.143.3.81:20081",
    "token": "49ac72f68d6e0d31688637c7b9733460c49ce5c6",
    "region_name": "tencent_ops",
    "namespace": "alauda",
    "db_engine": "postgres",  # mysql or postgres
    "wait_for_create_done": True,  # True: will waiting for service create done ,then create other
    "update_app": False  # True: update app for bind old lb info after app create done
}

Prefix = {
    "app_name_prefix": "app-" + Configs["region_name"].lower().replace("_", "-") + "-",
    "app_create_data_prefix": "app-data-" + Configs["region_name"] + "-",
    "cm_name_prefix": "cm-" + Configs["region_name"].lower().replace("_", "-") + "-",
    "app_cm_flag_file": "alauda-cm-",
    "lb_name_prefix": "lb-" + Configs["region_name"] + "-",
    "pipeline_name_prefix": "pipeline-" + Configs["region_name"] + "-",
    "task_file": "task_" + Configs["region_name"],
    "mock_task_file": "mock_task_" + Configs["region_name"],
    "mode_file": "mode_" + Configs["region_name"],
    "current_project_file": "project",
    "service_list_file": "service_list_" + Configs["namespace"] + "_" + Configs["region_name"],
    "service_detail_file": "service_" + Configs["namespace"] + "_" + Configs["region_name"] + "_",
    "app_list_file": "app_list_" + Configs["namespace"] + "_" + Configs["region_name"],
    "app_service_detail_file": "app_service_" + Configs["namespace"] + "_" + Configs["region_name"] + "_"
}

# trans will be skipped when service in ExcludedServiceNames
ExcludedServices = []  # ["test-aaa-1wsq", "test-bbb-cw11s"]

# trans will be skipped when service in ExcludedServiceNames
ExcludedApps = []  # ["test-app-1wsq", "test-app-cw11s"]


IncludeServiceStatus = [
    "Running",
    "Stopped",
    "StartError"
]

IncludeAppStatus = [
    "Running",
    "Stopped",
    "StartError",
    "PartialRunning"
]

URLS = {
    "get_region": "/v1/regions/{namespace}/{region_name}".format(
        namespace=Configs['namespace'], region_name=Configs['region_name']),
    "create_get_ns": "/v2/kubernetes/clusters/{region_name}/namespaces".format(region_name=Configs['region_name']),
    "get_resource_ns": "/v1/spaces/{namespace}/".format(
        namespace=Configs['namespace']),
    "get_projects": "/v1/projects/{namespace}/".format(namespace=Configs['namespace']),
    "get_svc_list": "/v1/services/{namespace}/?basic=false&"
                    "region_name={region_name}&page_size=100".format(
        namespace=Configs['namespace'], region_name=Configs['region_name']),
    "get_svc_v2": "/v2/services/?cluster={region_name}&name={service_name}".format(
        region_name=Configs['region_name'], service_name="{service_name}"),
    "get_svc_v2_instances": "/v2/services/{service_id}/instances".format(service_id="{service_id}"),
    "get_svc_by_id_v2": "/v2/services/{service_id}",
    "get_app_by_id": "/v2/apps/{app_id}",
    "get_subnets": "/v1/subnets/{namespace}?region_name={region_name}".format(
        namespace=Configs['namespace'], region_name=Configs['region_name']),
    "get_or_delete_svc_detail": "/v1/services/{namespace}/{service_id}".format(
        namespace=Configs['namespace'], service_id="{service_id}"),
    "get_or_delete_application_detail": "/v1/applications/{namespace}/{app_id}".format(
        namespace=Configs['namespace'], app_id="{app_id}"),
    "get_config_content": "/v1/configs/{namespace}/{filename}".format(
        namespace=Configs['namespace'], filename="{filename}"),
    "create_cm": "/v2/kubernetes/clusters/{region_name}/configmaps/".format(region_name=Configs['region_name']),
    "create_app": "/v2/apps",
    "stop_app": "/v2/apps/{app_id}/stop",
    "search_app": "/v2/apps/?cluster={region_name}&namespace=&name={app_name}".format(
        region_name=Configs["region_name"], app_name="{app_name}"),
    "get_lb": "/v1/load_balancers/{namespace}?region_name={region_name}&frontend=true".format(
        namespace=Configs['namespace'], region_name=Configs['region_name']),
    "lb_frontends": "/v1/load_balancers/{namespace}/{lb_name}/frontends".format(
        namespace=Configs['namespace'], lb_name="{lb_name}"),
    "lb_create_listener": "/v1/load_balancers/{namespace}/{lb_name_or_id}/frontends/{port}".format(
        namespace=Configs['namespace'], lb_name_or_id="{lb_name_or_id}", port="{port}"
    ),
    "lb_create_rule": "/v1/load_balancers/{namespace}/{lb_name_or_id}/frontends/{port}/rules".format(
        namespace=Configs['namespace'], lb_name_or_id="{lb_name_or_id}", port="{port}"),
    "lb_bind_svc_rule": "/v1/load_balancers/{namespace}/{lb_name_or_id}/frontends/{port}/rules/{rule_id}".format(
        namespace=Configs['namespace'], lb_name_or_id="{lb_name_or_id}", port="{port}", rule_id="{rule_id}"),
    "get_all_pipelines": "/v1/pipelines/{namespace}/config?page_size=100".format(namespace=Configs['namespace']),
    "get_or_update_pipeline": "/v1/pipelines/{namespace}/config/{pipeline_id}".format(
        namespace=Configs['namespace'], pipeline_id="{pipeline_id}"),
    "get_envfile": "/v1/env-files/{namespace}/{file_id}".format(namespace=Configs["namespace"], file_id="{file_id}"),
    "get_application_list": "/v1/applications/{namespace}?region={region_name}".format(
        namespace=Configs['namespace'], region_name=Configs["region_name"])
}
# kubectl get
GET_ALL_NS = "kubectl get ns --no-headers -o=custom-columns=NAME:.metadata.name"
GET_ALL_NS_JSON = "kubectl get ns -o json"
CREATE_CRD = "kubectl create -f crd.yaml"
