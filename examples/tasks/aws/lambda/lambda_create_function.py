# Credential section
import boto3
access_key = '@@{cred_aws.username}@@'
secret_key = '@@{cred_aws.secret}@@'

# Variables section
aws_region = '@@{aws_region_id}@@'

aws_iam_role_name = '@@{aws_iam_role_name}@@' # Existing role name
aws_s3_bucket_name = '@@{aws_s3_bucket_name}@@' # Existing bucket
aws_s3_bucket_file = '@@{aws_s3_bucket_file}@@' # Existing ZIP file with function
aws_lambda_name = '@@{aws_lambda_name}@@'
aws_lambda_runtime = '@@{aws_lambda_runtime}@@' # 'nodejs'|'nodejs4.3'|'nodejs6.10'|'nodejs8.10'|'nodejs10.x'|'nodejs12.x'|'java8'|'java11'|'python2.7'|'python3.6'|'python3.7'|'python3.8'|'dotnetcore1.0'|'dotnetcore2.0'|'dotnetcore2.1'|'dotnetcore3.1'|'nodejs4.3-edge'|'go1.x'|'ruby2.5'|'ruby2.7'|'provided'
aws_lambda_handler = '@@{aws_lambda_handler}@@'

# === DO NOT CHANGE AFTER THIS ===
DOCUMENTATION = r'''
---
An example of a YAML payload for using with @@{yaml_vars}@@

iam:
  RoleName: CalmBasicLambdaRole
lambda:
  FunctionName: mydemofunction
  Runtime: python3.8
  Handler: lambda_function.lambda_handler
  Code:
    S3Bucket: jg-calm
    S3Key: lambda_function.py.zip
'''

# Checking if YAML input is used. The dict below includes the minimum req for a fully functional LB
my_yaml = '''@@{yaml_vars}@@'''

if my_yaml == "":
    my_vars = {
        'iam': {
            'RoleName': aws_iam_role_name
        },
        'lambda': {
            'FunctionName': aws_lambda_name,
            'Runtime': aws_lambda_runtime,
            'Handler': aws_lambda_handler,
            'Code': {
                'S3Bucket': aws_s3_bucket_name,
                'S3Key': aws_s3_bucket_file
            }
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

lam = session.client('lambda')
iam = session.client('iam')

try:
    role = iam.get_role(**my_vars['iam'])

    # Create Lambda function
    response = lam.create_function(Role=role['Role']['Arn'],**my_vars['lambda'])
    # print('Creating Lambda function with name: {}'.format(my_vars['lambda']['FunctionName']))

    # lambda_complete_waiter = lam.get_waiter('function_active')

    # lambda_complete_waiter.wait(FunctionName=my_vars['lambda']['FunctionName'])
    print("Function {} created".format(my_vars['lambda']['FunctionName']))

except lam.exceptions.ClientError as error:
    raise error
