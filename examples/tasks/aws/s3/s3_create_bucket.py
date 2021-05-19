# Credential section
import boto3
access_key = '@@{cred_aws.username}@@'
secret_key = '@@{cred_aws.secret}@@'

# Variables section
aws_region = '@@{aws_region_id}@@'

aws_s3_bucket_name = '@@{aws_s3_bucket_name}@@'

# === DO NOT CHANGE AFTER THIS ===
DOCUMENTATION = r'''
---
An example of a YAML payload for using with @@{yaml_vars}@@

s3:
  Bucket: mybucket
'''

# Checking if YAML input is used. The dict below includes the minimum req for a Postgres database instance
my_yaml = '''@@{yaml_vars}@@'''

if my_yaml == "":
    my_vars = {
        's3': {
            'Bucket': aws_s3_bucket_name
        }
    }

else:
    my_vars = yaml.load(my_yaml)


# Authentication
session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name=aws_region
)

s3 = session.client('s3')

try:
    # Create S3 bucket
    response = s3.create_bucket(**my_vars['s3'])
    print('Creating S3 bucket: {}'.format(
        my_vars['s3']['Bucket']))

except s3.exceptions.ClientError as error:
    raise error

