# Credential section
from google.oauth2 import service_account
from googleapiclient import discovery

gcp_project = '@@{cred_gcp.username}@@'
# JSON keyfile - Use SSH Key credential to paste JSON keyfile
gcp_secret = @@{cred_gcp.secret}@@

# Authentication
credentials = service_account.Credentials.from_service_account_info(gcp_secret)

# Create client
# Compute API https://cloud.google.com/compute/docs/reference/rest/v1
client = discovery.build('compute', 'v1', credentials=credentials)

project = gcp_project

# Compute machineImages API https://cloud.google.com/compute/docs/reference/rest/v1/machineImages/list
request = client.machineImages().list(project=project)
while request is not None:
    response = request.execute()

    for image in response['items']:
        # TODO: Change code below to process each `image` resource:
        print(image)

    request = client.machineImages().list_next(
        previous_request=request, previous_response=response)
