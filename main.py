import services
import lb
import cm
import namespaces
import project
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
    if utils.check_region_version():
        print "\nPlease check configMap && update region version from v2 to v3;\n"
        exit(1)
    # init
    if utils.no_common_task_record("init_lb"):
        lb.init_lb()
        utils.task_common_record("init_lb")
    # by project
    projects = utils.get_projects()
    # add default
    projects.append({"name": ""})

    for pro in projects:
        # init project
        project.init_current_project(pro["name"])

        if utils.no_task_record("init_services"):
            services.init_svc_list()
            utils.task_record("init_services")
        if utils.no_task_record("init_service_detail"):
            services.init_svc_detail()
            utils.task_record("init_service_detail")

        if utils.no_task_record("init_cm"):
            cm.init_cm()
            utils.task_record("init_cm")

        if utils.no_task_record("sync_namespace"):
            namespaces.sync_ns()
            utils.task_record("sync_namespace")
        if utils.no_task_record("create_cm"):
            cm.create_cm()
            utils.task_record("create_cm")
        # service trans
        services.main()
    lb.main()

