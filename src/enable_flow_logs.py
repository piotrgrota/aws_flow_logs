import boto3
import os


def create_log_group(logs_client):
    log_group_name = os.environ['FLOWLOGS_GROUP_NAME']
    print('FLOWLOGS_GROUP_NAME: ' + os.environ['FLOWLOGS_GROUP_NAME'])
    print('VPC Flow Logs are DISABLED')
    response = logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
    if len(response[u'logGroups']) == 0:
        print("Create Log Group - " + log_group_name)
        logs_client.create_log_group(logGroupName = log_group_name)

def create_flow_logs(client,vpc_id):
    log_group_name = os.environ['FLOWLOGS_GROUP_NAME']
    role_arn = os.environ['ROLE_ARN']
    response = client.create_flow_logs(
        DeliverLogsPermissionArn=role_arn,
        LogGroupName=log_group_name,
        ResourceIds=[
            vpc_id
        ],
        ResourceType='VPC',
        TrafficType='ALL',
        LogDestinationType="cloud-watch-logs"
    )
    print('Created Flow Logs: ' + response['FlowLogIds'][0])

def enable_vpc_flow_logs(vpc_id , region):
    ec2_client = boto3.client('ec2', region_name = region)
    logs_client = boto3.client('logs', region_name = region)

    response = ec2_client.describe_flow_logs(
        Filter=[
            {
                'Name': 'resource-id',
                'Values': [
                    vpc_id,
                ]
            },
        ],
    )
    if len(response[u'FlowLogs']) != 0:
        print('VPC Flow Logs are ENABLED in region - ' + region)
    else:
        create_log_group(logs_client)
        create_flow_logs(ec2_client, vpc_id)


def lambda_handler(event, context):
    vpc_id = event['detail']['responseElements']['vpc']['vpcId']
    region = event['region']
    print('VPC: ' + vpc_id)
    print('Region: ' + region)

    enable_vpc_flow_logs(vpc_id, region)

    