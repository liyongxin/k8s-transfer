import os
import sys
import json
sys.path.append("..")
import requests
import consts
import project


def send_request(method, url, params=None, specific_project=None):
    """
    send post request,if success return json-obj else raise exception
    :param specific_project:
    :param method:
    :param url:
    :param params:
    :return:
    """
    pre_url = consts.Configs['api_url']
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token " + consts.Configs['token']
    }
    try:
        current_project = project.get_current_project()
        if specific_project:
            current_project = specific_project
        if url.count("?") > 0:
            url = url + "&project_name=" + current_project
        else:
            url = url + "?project_name=" + current_project
        req_url = pre_url + url  # "http://localhost/cgi-bin/python_test/test.py"
        print "\nbegin request url="+req_url+"&&params="+str(params)
        if method == 'GET':
            resp = requests.get(req_url, headers=headers)
        elif method == 'POST':
            resp = requests.post(req_url, data=json.dumps(params), headers=headers)
        elif method == 'PUT':
            resp = requests.put(req_url, data=json.dumps(params), headers=headers)
        elif method == 'PATCH':
            resp = requests.patch(req_url, data=json.dumps(params), headers=headers)
        elif method == 'DELETE':
            resp = requests.delete(req_url, headers=headers)
        else:
            raise Exception('wrong request type')
        # print resp.json()
        # get json-obj
        if resp.content:
            response = resp.json()
            # check response
            if isinstance(response, list):
                return response
            elif isinstance(response, dict) and "errors" in response:
                print response["errors"][0]["message"]
                writer = open("error_urls", "a+")
                writer.write("\n\nERROR!!!!!! response="+str(response)+"\nurl="+req_url+"\nparams="+str(params)+"\n\n")
                writer.close()
                print response
                return response
                # raise Exception(res["errors"][0]["message"])
            elif isinstance(response, dict) and "message" in response and response["message"] == "SUCCESS":
                return response["data"] or response
            else:
                return response
        else:
            return ""
    except Exception:
        raise


def get_region_info(key=None):
    data = send_request("GET", consts.URLS["get_region"])
    if key and key in data:
        return data[key]
    return data


def get_projects():
    projects = send_request("GET", consts.URLS["get_projects"])
    default_project = {
        "name": "",
        "uuid": ""
    }
    # add default project(no project)
    projects.append(default_project)
    return projects


def get_current_project():
    return project.get_current_project()


def get_current_folder():
    return project.get_current_folder()


def get_default_folder():
    return project.get_default_folder()


def check_region_version():
    if get_region_info("platform_version") == "v2":
        return True
    return False


def task_record(task):
    task = project.get_current_project() + "_" + task
    task_file = get_task_file()
    if not os.path.exists(task_file):
        os.mknod(task_file)
    file_writer(task_file, task + "\n", "a+")
    print '\n==============' + task + ' has finished===================\n'


def no_task_record(task):
    task = project.get_current_project() + "_" + task
    task_file = get_task_file()
    if not os.path.exists(task_file):
        os.mknod(task_file)
    reader = open(task_file, "r")
    tasks = reader.readlines()
    reader.close()
    for task_solve in tasks:
        if task_solve == (task + "\n") or task_solve == task:
            print '\n==============' + task + ' has done, will be skipped ==============\n'
            return False
    print '\n==============' + task + ' starting to execute==============\n'
    return True


def init_exec_mode(value):
    mode_file = consts.Prefix["mode_file"]
    if not os.path.exists(mode_file):
        os.mknod(mode_file)
    file_writer(mode_file, value, "w")
    print '\n==============init exec mode {}===================\n'.format(value)


def get_exec_mode():
    mode_file_name = consts.Prefix["mode_file"]
    reader = open(mode_file_name, "r")
    mode = reader.readline()
    reader.close()
    return mode


def task_common_record(task):
    task_file = get_task_file()
    if not os.path.exists(task_file):
        os.mknod(task_file)
    file_writer(task_file, task + "\n", "a+")
    print '\n==============' + task + ' has finished===================\n'


def get_task_file():
    mode = get_exec_mode()
    if mode == "prod":
        return consts.Prefix["task_file"]
    elif mode == "mock":
        return consts.Prefix["mock_task_file"]
    else:
        exit("ERROR!! no mode match prod and mock")


def no_common_task_record(task):
    task_file = get_task_file()
    if not os.path.exists(task_file):
        os.mknod(task_file)
    reader = open(task_file, "r")
    tasks = reader.readlines()
    reader.close()
    for task_solve in tasks:
        if task_solve == (task + "\n") or task_solve == task:
            print '\n==============' + task + ' has done, will be skipped ==============\n'
            return False
    print '\n==============' + task + ' starting to execute==============\n'
    return True


def file_writer(filename, data, mode="w"):
    writer = open(filename, mode)
    if isinstance(data, list) or isinstance(data, dict):
        writer.write(json.dumps(data))
    else:
        writer.write(data)
    writer.close()


def file_reader(filename):
    reader = open(filename, "r")
    data = json.load(reader)
    reader.close()
    return data


if __name__ == '__main__':
    url = consts.URLS["create_get_ns"]
    data = {
        "cluster": {
            "uuid": "",
            "name": "htzq"
        },
        "resource": {
            "name": "default--dev-c"
        }
    }
    data = send_request("POST", url, specific_project="yxli-pro-2")
    print data
