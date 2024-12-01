import boto3
import os
from botocore.exceptions import ClientError

def table_exists(dynamodb, table_name):
    try:
        dynamodb.describe_table(TableName=table_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return False
        raise

def create_table(dynamodb, table_name):
    dynamodb.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    waiter = dynamodb.get_waiter('table_exists')
    waiter.wait(TableName=table_name)
    print(f"Created table {table_name}")

def initialize_database():
    dynamodb = boto3.client('dynamodb', endpoint_url=os.environ.get('DYNAMODB_ENDPOINT_URL'))
    tables = ['Cards', 'BoardList']
    
    for table_name in tables:
        if not table_exists(dynamodb, table_name):
            create_table(dynamodb, table_name)
        else:
            print(f"Table {table_name} already exists") 
