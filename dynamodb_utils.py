import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', endpoint_url=os.environ['DYNAMO_URL'])


def get_cards():
    table = dynamodb.Table('Cards')
    response = table.scan()
    return response.get('Items', [])


def get_lists():
    table = dynamodb.Table('BoardList')
    response = table.scan()
    return response.get('Items', [])


# # Create the 'Cards' table
# table = dynamodb.create_table(
#     TableName='Cards',
#     KeySchema=[
#         {
#             'AttributeName': 'id',
#             'KeyType': 'HASH'
#         },
#     ],
#     AttributeDefinitions=[
#         {
#             'AttributeName': 'id',
#             'AttributeType': 'S'
#         },
#     ],
#     ProvisionedThroughput={
#         'ReadCapacityUnits': 5,
#         'WriteCapacityUnits': 5
#     }
# )

# Wait for the table to be created (optional)


# aws dynamodb scan --table-name Cards --endpoint-url http://localhost:8000
# aws dynamodb list-tables --endpoint-url http://localhost:8000


# table_name = 'BoardList'

# table = dynamodb.create_table(
#     TableName=table_name,
#     KeySchema=[
#         {
#             'AttributeName': 'id',
#             'KeyType': 'HASH'  # HASH type for the primary key
#         }
#     ],
#     AttributeDefinitions=[
#         {
#             'AttributeName': 'id',
#             'AttributeType': 'S'  # 'S' for string attribute type
#         }
#     ],
#     ProvisionedThroughput={
#         'ReadCapacityUnits': 5,  # Adjust according to your needs
#         'WriteCapacityUnits': 5  # Adjust according to your needs
#     }
# )

# wait
# table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
