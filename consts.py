
Configs = {
    "api_url": "http://140.143.10.131:20081",
    "token": "75f99be461c38fe04376bdc155a0b443231fe498",
    "region_name": "lbx2",
    "namespace": "alauda",
    "db_engine": "mysql"  # mysql or postgres
}

Prefix = {
    "app_name_prefix": "app-" + Configs["region_name"] + "-",
    "cm_name_prefix": "cm-" + Configs["region_name"] + "-",
    "lb_name_prefix": "lb-" + Configs["region_name"] + "-",
    "pipeline_name_prefix": "pipeline-" + Configs["region_name"] + "-",
    "task_file": "task_" + Configs["region_name"],
    "current_project_file": "project",
    "service_list_file": "service_list_" + Configs["namespace"] + "_" + Configs["region_name"],
    "service_detail_file": "service_" + Configs["namespace"] + "_" + Configs["region_name"] + "_"
}

# trans will be skipped when service in ExcludedServiceNames
ExcludedServices = []

IncludeServiceStatus = [
    "Running",
    "Stopped",
    "StartError"
]

URLS = {
    "get_region": "/v1/regions/{namespace}/{region_name}".format(
        namespace=Configs['namespace'], region_name=Configs['region_name']),
    "create_get_ns": "/v2/namespaces/",
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
    "get_config_content": "/v1/configs/{namespace}/{filename}".format(
        namespace=Configs['namespace'], filename="{filename}"),
    "create_cm": "/v2/configmaps/",
    "create_app": "/v2/apps",
    "stop_app": "/v2/apps/{app_id}/stop",
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
    "get_envfile": "/v1/env-files/{namespace}/{file_id}".format(namespace=Configs['namespace'], file_id="{file_id}")
}
# kubectl get
GET_ALL_NS = "kubectl get ns --no-headers -o=custom-columns=NAME:.metadata.name"
GET_ALL_NS_JSON = "kubectl get ns -o json"

