import requests
from datetime import datetime

CONTENT_URL = "@@{ntnx_calm_object_uri}@@"
CONTENT_KIND = "@@{ntnx_calm_object_kinds}@@"
CONTENT_NAME = "@@{ntnx_calm_object_kind}@@"


base_url = "https://localhost:9440/api/nutanix/v3"
authstr = "Bearer @@{calm_jwt}@@"
project = "@@{ntnx_calm_import_to_project}@@"

# Get Project UUID
headers = {"Content-Type": "application/json"}
headers.update({"Authorization": authstr})
endpoint_url = "/".join((base_url, "projects", "list"))
payload = {"filter": "name=={project}".format(project=project)}

res = requests.post(endpoint_url,headers=headers,json=payload,verify=False)
project_uuid = res.json()["entities"][0]["metadata"]["uuid"]

# Download Content
headers.pop("Authorization")
res = requests.get(CONTENT_URL, headers=headers)
content = res.content

# Upload Content
headers.update({"Authorization": authstr})

params = {"filter": "name=={};state!=DELETED".format(CONTENT_NAME)}
endpoint_url = "/".join((base_url, CONTENT_KIND, "list"))
res = requests.post(endpoint_url,headers=headers,json=params,verify=False)
if len(res.json()["entities"]) > 0:
    if @@{ntnx_calm_object_overwrite}@@:
        bp_uuid = res.json()["entities"][0]["metadata"]["uuid"]
        endpoint_url = "/".join((base_url, CONTENT_KIND, bp_uuid))
        res = requests.delete(endpoint_url,headers=headers,verify=False)
    else:
        CONTENT_NAME = CONTENT_NAME + "_" + datetime.now().strftime("%s")

headers.pop("Content-Type")
endpoint_url = "/".join((base_url, CONTENT_KIND, "import_file"))
payload = {"filter": "name=={project}".format(project=project)}
files = {'file': ('blob', content)}
payload = {"name": CONTENT_NAME, "project_uuid": project_uuid}

res = requests.post(endpoint_url,headers=headers,files=files,data=payload,verify=False)

if res.ok:
    print("Content uploaded")
    
else:
    print("Request failed", res.text)
    exit(1)