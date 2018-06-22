import os
import consts

project_file = consts.Prefix["current_project_file"]


def get_current_project():
    if not os.path.exists(project_file):
        os.mknod(project_file)
    reader = open(project_file, "r")
    project = reader.readline()
    reader.close()
    return project


def get_current_folder():
    folder = get_current_project()
    if not folder:
        folder = "default"
    if not os.path.exists(folder):
        os.mkdir(folder)
    return folder + "/"


def get_project_by_svc_name(svc_name):
    svc_file_name = consts.Prefix["service_detail_file"] + svc_name
    cmd = "find . -name " + svc_file_name + " |awk -F \"/\" '{print $2}'"
    project = os.popen(cmd).readline().split("\n")[0]
    return project


def init_current_project(project=None):
    folder = project
    if not project:
        project = ""
        folder = "default"
    writer = open(project_file, "w")
    writer.write(project)
    writer.close()
    if not os.path.exists(folder):
        os.mkdir(folder)


if __name__ == '__main__':
    pass
