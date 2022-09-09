# Azure with Nutanix NCM Self-Service

## Authentication & Client

```python
from azure.common.credentials import ServicePrincipalCredentials

az_subscription_id = '@@{azure_subscription_id}@@'
az_client_id = '@@{azure_client_id}@@'
az_tenant_id = '@@{azure_tenant_id}@@'
az_secret = '@@{azure_secret}@@'

# Authentication
def get_credentials():
    subscription_id = az_subscription_id
    credentials = ServicePrincipalCredentials(
        client_id=az_client_id,
        secret=az_secret,
        tenant=az_tenant_id
    )
    return credentials, subscription_id

credentials, subscription_id = get_credentials()

# Create client - Site Recovery API https://docs.microsoft.com/en-us/python/api/overview/azure/mgmt-recoveryservicesbackup-readme?view=azure-python
from azure.mgmt.recoveryservicesbackup import RecoveryServicesBackupClient
client = RecoveryServicesBackupClient(credentials, subscription_id)
```
