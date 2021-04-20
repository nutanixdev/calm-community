# Credential section
import boto3
access_key = '@@{cred_aws.username}@@'
secret_key = '@@{cred_aws.secret}@@'

# Variables section
aws_region = '@@{aws_region_id}@@'

aws_vpc_id = '@@{aws_vpc_id}@@'

aws_elb_name = '@@{aws_elb_name}@@'
aws_subnet_id = '@@{aws_subnet_id}@@'
aws_sg_id = '@@{aws_sg_id}@@'
aws_elb_scheme = '@@{aws_elb_scheme}@@'
aws_elb_type = '@@{aws_elb_type}@@'
aws_elb_ipaddresstype = '@@{aws_elb_ipaddresstype}@@'

aws_tg_name = '@@{aws_tg_name}@@'
aws_tg_protocol = '@@{aws_tg_protocol}@@'
aws_tg_port = '@@{aws_tg_port}@@'
aws_tg_healthcheckprotocol = '@@{aws_tg_healthcheckprotocol}@@'
aws_tg_targettype = '@@{aws_tg_targettype}@@'

aws_listener_protocol = '@@{aws_listener_protocol}@@'
aws_listener_port = '@@{aws_listener_port}@@'
aws_listener_defaultactions_type = '@@{aws_listener_defaultactions_type}@@'

# === DO NOT CHANGE AFTER THIS ===
DOCUMENTATION = r'''
---
An example of a YAML payload for using with @@{yaml_vars}@@

vpc:
  id: vpc-29354341
elb:
  Name: myelb
  Subnets:
  - subnet-4e314927
  - subnet-6bff3427
  SecurityGroups:
  - sg-0022176bcc2307493
  Scheme: internet-facing
  Type: application
  IpAddressType: ipv4
target_group:
  Name: mytarget
  Protocol: HTTP
  Port: 80
  VpcId: vpc-29354341
  HealthCheckProtocol: HTTP
  TargetType: ip
listener:
  Protocol: HTTP
  Port: 80
  DefaultActions:
  - Type: forward
'''

# Checking if YAML input is used. The dict below includes the minimum req for a fully functional LB
my_yaml = '''@@{yaml_vars}@@'''

if my_yaml == "":
    my_vars = {
        'vpc': {
            'id': aws_vpc_id
        },
        'elb': {
            'Name': aws_elb_name,
            'Subnets': aws_subnet_id.split(','),
            'SecurityGroups': aws_sg_id.split(','),
            'Scheme': aws_elb_scheme,
            'Type': aws_elb_type,
            'IpAddressType': aws_elb_ipaddresstype
        },
        'target_group': {
            'Name': aws_tg_name,
            'Protocol': aws_tg_protocol,
            'Port': int(aws_tg_port),
            'VpcId': aws_vpc_id,
            'HealthCheckProtocol': aws_tg_healthcheckprotocol,
            'TargetType': aws_tg_targettype,
        },
        'listener': {
            'Protocol': aws_listener_protocol,
            'Port': int(aws_listener_port),
            'DefaultActions': [
                {'Type': aws_listener_defaultactions_type}
            ]
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

elb = session.client('elbv2')

try:
    # Create ELB
    response = elb.create_load_balancer(**my_vars['elb'])
    print('Creating ELB instance with name: {}'.format(my_vars['elb']['Name']))

    elb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
    elb_name = response['LoadBalancers'][0]['LoadBalancerName']
    elb_dns = response['LoadBalancers'][0]['DNSName']

    elb_complete_waiter = elb.get_waiter('load_balancer_available')

    elb_complete_waiter.wait(LoadBalancerArns=[elb_arn])
    print("Load balancer {} created".format(elb_name))
    print("DNS name={}".format(elb_dns))

    # Create ELB Target Group
    response = elb.create_target_group(**my_vars['target_group'])

    elb_target_arn = response['TargetGroups'][0]['TargetGroupArn']

    # Create ELB Listener
    my_vars['listener']['LoadBalancerArn'] = elb_arn
    my_vars['listener']['DefaultActions'][0]['TargetGroupArn'] = elb_target_arn
    elb.create_listener(**my_vars['listener'])
except elb.exceptions.ClientError as error:
    raise error
