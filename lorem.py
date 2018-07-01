import os
from urlparse import urljoin

import requests


subnetCrd = '''
apiVersion: alauda.io/v1
kind: Subnet
metadata:
  name: {subnet_name}
spec:
  subnet_name: {subnet_name}
  namespace:
  project_name: {project_name}
  cidr_block: {cidr_block}
  gateway: {gateway}
  created_at:
  updated_at:
  created_by:
'''

ipCrd = '''
apiVersion: alauda.io/v1
kind: IP
metadata:
  name: {address}
  labels:
    subnet: {subnet_name}
    used: false
spec:
  used: False
  fresh: True
  subnet_name: {subnet_name}
  service_id:
  service_name:
'''

# Configs = {
#     "api_url": "http://40.83.73.194:20081",
#     "token": "06b92f316be5462f486819ba947f931d4c9e59fc",
#     "region_name": "global",
#     "namespace": "alauda",
# }
Configs = {
    "api_url": "http://api.alauda.cn",
    "token": "abb1d85a2ad1763640c52e9f5f7f3a8794826a71",
    "region_name": "monkey_cluster",
    "namespace": "alaudaorg",
}

SUBNET_URL = "/v1/subnets/{namespace}"
IPS_URL = "/v1/subnets/{namespace}/{subnet_name}/private_ips"
CRD_DIR = os.path.expanduser("~/crd/")


class Request(object):
    def __init__(self, api_url, token):
        self.session = requests.Session()
        self.base_url = api_url
        self.session.headers.update({'Authorization': 'token ' + token})

    def get(self, url, *args, **kwargs):
        return self.session.get(urljoin(self.base_url, url), *args, **kwargs)


if not os.path.exists(CRD_DIR):
    os.makedirs(CRD_DIR)

myrequest = Request(Configs['api_url'], Configs['token'])
subnets = myrequest.get(SUBNET_URL.format(namespace=Configs['namespace']),
                        params={'region_name': Configs['region_name']})
for subnet in subnets.json():
    with open(os.path.join(CRD_DIR, subnet['subnet_name']), 'w') as f:
        f.write(subnetCrd.format(**subnet))
    ips = myrequest.get(IPS_URL.format(namespace=Configs['namespace'],
                                       subnet_name=subnet['subnet_name']))
    for ip in ips.json():
        with open(os.path.join(CRD_DIR, ip['address']), 'w') as f:
            f.write(ipCrd.format(**ip))

for crd in os.listdir(CRD_DIR):
    print("create crd {}".format(crd))
    os.system("kubectl apply -f {}".format(os.path.join(CRD_DIR, crd)))
