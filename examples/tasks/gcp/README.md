# GCP with Nutanix NCM Self-Service

## Authentication & Client

```python
from google.oauth2 import service_account

gcp_project = '@@{cred_gcp.username}@@'
gcp_secret = @@{cred_gcp.secret}@@ # JSON keyfile - Use SSH Key credential to paste JSON keyfile
gcp_zone = '@@{gcp_zone_id}@@' # Not required for every service

# Authentication
credentials = service_account.Credentials.from_service_account_info(gcp_secret)

# Create client - compute API https://cloud.google.com/compute/docs/reference/rest/v1
from googleapiclient import discovery
client = discovery.build('compute', 'v1', credentials=credentials)
```
