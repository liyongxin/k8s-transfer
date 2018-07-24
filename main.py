import services
import lb
import cm
import namespaces
import project
import consts
import pipeline
import applications
from utils import utils

if __name__ == '__main__':
    """
    init service data
    init config data
    init lb data
    trans v2 to v3
    sync namespace
    single service trans (delete && create)
    confirm
    """
    # init exec mode
    utils.init_exec_mode("prod")
    if utils.check_region_version():
        print "update app_region set platform_version = 'v3' where name='{region_name}'".\
            format(region_name=consts.Configs["region_name"])
        print "\nPlease execute sql to update region version from v2 to v3;\n"
        exit(1)

    # init lb info
    if utils.no_common_task_record("init_lb_list"):
        lb.init_lb_list()
        utils.task_common_record("init_lb_list")
    # transfer by project
    projects = utils.get_projects()
    for pro in projects:
        # init project
        project.init_current_project(pro["name"])

        # build sql for table jakiro.resources_resource, should be executed by hands
        if utils.no_task_record("sync_namespace"):
            namespaces.sync_ns_v2()
            # print "Please execute sql for jakiro db by hands;\n"
            utils.no_task_record("sync_namespace")

        if utils.no_task_record("init_services"):
            services.init_svc_list()
            utils.task_record("init_services")
        if utils.no_task_record("init_service_detail"):
            services.init_svc_detail()
            utils.task_record("init_service_detail")

        if utils.no_task_record("init_service_lb"):
            lb.init_svc_lb()
            utils.task_record("init_service_lb")

        if utils.no_task_record("init_applications"):
            applications.init_app_list()
            utils.task_record("init_applications")
        if utils.no_task_record("init_application_detail"):
            applications.init_app_svc_detail()
            utils.task_record("init_application_detail")

        if utils.no_task_record("sync_applications_ns"):
            namespaces.sync_app_ns()
            utils.task_record("sync_applications_ns")

        if utils.no_task_record("init_applications_service_lb"):
            lb.init_app_svc_lb()
            utils.task_record("init_applications_service_lb")

        if utils.no_task_record("init_cm"):
            cm.init_cm()
            cm.init_app_cm()
            utils.task_record("init_cm")

        if utils.no_task_record("create_cm"):
            cm.create_cm()
            utils.task_record("create_cm")
        # service trans
        services.main()
        applications.main()
        pipeline.main()
        if utils.no_task_record("update_jakiro_resource"):
            services.build_volume_sql()
            utils.task_record("update_jakiro_resource")


