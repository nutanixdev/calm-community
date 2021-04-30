# AWS with Calm

## Authentication & Client

```python
import boto3

access_key = '@@{cred_aws.username}@@'
secret_key = '@@{cred_aws.secret}@@'
aws_region = '@@{aws_region_id}@@'

# Authentication
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=aws_region
)

client = session.client('rds') # i.e. RDS client, replace rds with other AWS services
```
