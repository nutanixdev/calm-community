# Credential section
import boto3
access_key = '@@{cred_aws.username}@@'
secret_key = '@@{cred_aws.secret}@@'

# Variables section
aws_region = '@@{aws_region_id}@@'

aws_rds_dbinstanceidentifier = '@@{aws_rds_dbinstanceidentifier}@@'
aws_rds_dbinstanceclass = '@@{aws_rds_dbinstanceclass}@@'
aws_rds_engine = '@@{aws_rds_engine}@@'
aws_rds_masterusername = '@@{aws_rds_masterusername}@@'
aws_rds_masteruserpassword = '@@{aws_rds_masteruserpassword}@@'
aws_rds_allocatedstorage = '@@{aws_rds_allocatedstorage}@@'

# === DO NOT CHANGE AFTER THIS ===
DOCUMENTATION = r'''
---
An example of a YAML payload for using with @@{yaml_vars}@@

rds:
  DBInstanceIdentifier: myrds
  DBInstanceClass: db.t2.micro
  Engine: postgres
  MasterUsername: postgres
  MasterUserPassword: postgres
  AllocatedStorage: 20
'''

# Checking if YAML input is used. The dict below includes the minimum req for a Postgres database instance
my_yaml = '''@@{yaml_vars}@@'''

if my_yaml == "":
    my_vars = {
        'rds': {
            'DBInstanceIdentifier': aws_rds_dbinstanceidentifier,
            'DBInstanceClass': aws_rds_dbinstanceclass,
            'Engine': aws_rds_engine,
            'MasterUsername': aws_rds_masterusername,
            'MasterUserPassword': aws_rds_masteruserpassword,
            'AllocatedStorage': int(aws_rds_allocatedstorage)
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

rds = session.client('rds')

try:
    # Create RDS
    response = rds.create_db_instance(**my_vars['rds'])
    print('Creating RDS instance with ID: {}'.format(
        my_vars['rds']['DBInstanceIdentifier']))

    waiter = rds.get_waiter('db_instance_available')
    waiter.wait(DBInstanceIdentifier=aws_rds_dbinstanceidentifier)
    print('RDS instance with ID: {} successfully created'.format(
        my_vars['rds']['DBInstanceIdentifier']))

except rds.exceptions.ClientError as error:
    raise error
