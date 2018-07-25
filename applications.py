import time
import consts
import services
import lb
import namespaces
from os import path
from utils import utils


def get_app_list_for_current_project(results=None):
    if results is None:
        results = []
    app_list = utils.send_request('GET', consts.URLS['get_application_list'])
    results.extend(app_list)
    # has to be len(app_list)
    if len(app_list) >= 100:
        get_app_list_for_current_project(results)
    return results


def get_app_svc_namespace(app_svc_detail):
    space_name = app_svc_detail["space_name"]
    return app_svc_detail["app_name"] + "-" + space_name if space_name else "default"


def init_app_list():
    app_list = get_app_list_for_current_project(results=[])
    file_name = utils.get_current_folder() + consts.Prefix["app_list_file"]
    utils.file_writer(file_name, app_list)


def init_app_svc_detail():
    app_list = get_app_list()
    for app in app_list:
        for app_service in app["services"]:
            services.svc_detail_handler(app_service)


def get_app_service_detail(svc_id):
    svc_detail = {}
    file_name = utils.get_current_folder() + consts.Prefix["app_service_detail_file"] + svc_id
    if path.exists(file_name):
        svc_detail = utils.file_reader(file_name)
    else:
        raise Exception("app service detail file {} doesn't exists!".format(file_name))
    return svc_detail


def get_app_list():
    results = []
    file_name = utils.get_current_folder() + consts.Prefix["app_list_file"]
    if path.exists(file_name):
        results = utils.file_reader(file_name)
    else:
        raise Exception("app list file doesn't exists!")
    return results


def delete_old_application(app_id):
    utils.send_request("DELETE", consts.URLS["get_or_delete_application_detail"].format(app_id=app_id))


def get_v1_app_by_api(app_id):
    return utils.send_request("GET", consts.URLS["get_or_delete_application_detail"].format(app_id=app_id))


def trans_app_data(app):
    app_data = {
        "resource": {
            "create_method": "UI"
        },
        "kubernetes": []
    }
    app_data["resource"]["name"] = consts.Prefix["app_name_prefix"] + app["app_name"].lower()

    app_namespace_name = app["app_name"] + "-" + app["space_name"] if app["space_name"] else "default"

    app_data["namespace"] = {
        "name": app_namespace_name,
        "uuid": namespaces.get_alauda_ns_by_name(app_namespace_name)["uid"]
    }
    app_data["cluster"] = {
        "name": app["region_name"],
        "uuid": app["region_uuid"]
    }
    for app_service in app["services"]:
        app_service_detail = get_app_service_detail(app_service["uuid"].lower())
        app_data["kubernetes"].extend(services.trans_pod_controller(app_service_detail))
        if len(app_service_detail["mount_points"]) > 0:
            app_data["resource"]["create_method"] = "yaml"
    app_create_data_file = utils.get_current_folder() + consts.Prefix["app_create_data_prefix"] + app["app_name"]
    utils.file_writer(app_create_data_file, app_data)
    return app_data


def main():
    app_list = get_app_list()
    for app in app_list:
        app_name = app["app_name"].lower()
        app_status = app["current_status"]

        task_single_app = "trans_app_{app_id}_{app_name}".format(app_id=app["uuid"], app_name=app_name)
        if utils.no_task_record(task_single_app):
            # skipped excluded services in consts.ExcludedServiceNames
            if app_name in consts.ExcludedApps:
                print "skipped app {} because configed in consts.ExcludedApps".format(app_name)
                continue
            if app_status not in consts.IncludeAppStatus:
                raw_tips = "{app_name} status is {app_status}, input Yes/No for continue or skip ". \
                    format(app_name=app_name, app_status=app_status)
                answer = raw_input(raw_tips)
                if answer.lower() == "no":
                    print "skipped app {} because current_status is {}".format(app_name, app_status)
                    continue
            print "begin trans application data to new app data for application {}".format(app_name)
            app_data = trans_app_data(app)
            print "app data for application {}".format(app_name)
            print app_data
            print "\nbegin delete application old application {}".format(app_name)
            delete_old_application(app["uuid"])
            print "\nwaiting application {} for delete ".format(app_name)
            for count in range(50):
                time.sleep(3)
                v1_application_info = get_v1_app_by_api(app["uuid"])
                if isinstance(v1_application_info, dict) and "errors" in v1_application_info:
                    print "\n app {} delete done".format(app_name)
                    break

            print "\nbegin create app for application {} ".format(app_name)
            app_info = services.create_app(app_data)
            if isinstance(app_info, dict) and "errors" in app_info:
                search_apps = services.get_app_by_name(app_data["resource"]["name"])
                if len(search_apps) == 0:
                    exit("create app error!!!!")
                app_info = search_apps[0]
            is_running = True
            if app_status not in ["Running", "Warning"]:
                is_running = False
                content = "{}-{}-{}\n".format(utils.get_current_project(), app_name, app_status)
                utils.file_writer("not_running_app.list", content, "a+")
                print "app {} current status is {}, will not waiting for created done".format(app_name,app_status)
            if consts.Configs["use_lb"] and is_running:
                # print app_info
                print "\nwaiting new app {} for create ".format(app_name)
                create_done = False
                for count in range(50):
                    time.sleep(3)
                    app = services.get_app_by_api(app_info["resource"]["uuid"])
                    app_current_state = app["resource"]["status"]
                    if app_current_state == "Running":
                        print "\n app {} create done".format(app_name)
                        create_done = True
                        break
                    else:
                        print "\n app {} current status is {}, continue waiting...".format(app_name, app_current_state)
                if not create_done:
                    print "application create too slow , please check!"
                    # exit(1)
                if create_done and consts.Configs["update_app"]:
                    # begin update app for bind old tag
                    app = services.get_app_by_api(app_info["resource"]["uuid"])
                    update_done = False
                    services.update_app(app)
                    print "\nwaiting app {} for update ".format(app_name)
                    for count in range(50):
                        time.sleep(3)
                        app = services.get_app_by_api(app_info["resource"]["uuid"])
                        app_current_state = app["resource"]["status"]
                        if app_current_state == "Running":
                            print "\n app {} update done".format(app_name)
                            update_done = True
                            break
                        else:
                            print "\n app {} current status is {}, continue waiting...".format(app_name,
                                                                                               app_current_state)
                    if not update_done:
                        print "application update too slow , please check!"
                        # exit(1)
            # handle lb binding
            for app_service in app["services"]:
                if "resource" in app_service and "name" in app_service["resource"]:
                    lb.handle_lb_for_svc(app_service["resource"]["name"].lower())
                elif "service_name" in app_service:
                    lb.handle_lb_for_svc(app_service["service_name"].lower())
            # if service_status == "Stopped":
            #    app_id = app_info["resource"]["uuid"]
            #    utils.send_request("PUT", consts.URLS["stop_app"].format(app_id=app_id))
            utils.task_record(task_single_app)
            print "!!!!!Status Confirm: old app status is {}, " \
                  "please check if should change by hands".format(app_status)
            exit(1)


if __name__ == '__main__':
    pass
