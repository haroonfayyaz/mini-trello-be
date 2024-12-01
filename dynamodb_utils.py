import os
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', endpoint_url=os.environ['DYNAMODB_ENDPOINT_URL'])
dynamodb_client = boto3.client('dynamodb', endpoint_url=os.getenv('DYNAMODB_ENDPOINT_URL'))


def get_cards():
    table = dynamodb.Table('Cards')
    response = table.scan()
    return response.get('Items', [])


def get_lists():
    table = dynamodb.Table('BoardList')
    response = table.scan()
    return response.get('Items', [])

def fetch_card_from_data_store(card_id, attributes_to_fetch=None):
    # Create the base request parameters
    request_params = {
        'TableName': 'Cards',
        'Key': {'id': {'S': card_id}}
    }

    # Only add ProjectionExpression if attributes_to_fetch is provided
    if attributes_to_fetch:
        request_params['ProjectionExpression'] = ", ".join(attributes_to_fetch)

    # Make the DynamoDB request
    response = dynamodb_client.get_item(**request_params)

    item = response.get('Item')
    
    if item:
        result = {}
        for key, value in item.items():
            if 'S' in value:
                result[key] = value['S']
            elif 'N' in value:
                result[key] = int(value['N'])
            elif 'L' in value:
                result[key] = value['L']
            elif 'M' in value:
                result[key] = value['M']
        return result
    else:
        return None


def fetch_lists_with_card(card_id):
    try:
        # Initialize an empty list to store the lists containing the card
        lists_with_card = []

        # Scan the 'BoardList' table in DynamoDB
        response = dynamodb_client.scan(
            TableName='BoardList'
        )

        # Iterate through each item in the response
        for item in response.get('Items', []):
            # Check if the 'cards' attribute contains the specified card_id
            cards = item.get('cards', {}).get('L', [])
            for card in cards:
                card_item = card.get('M', {})
                if 'id' in card_item and card_item['id'].get('S') == card_id:
                    list_item = {
                        'id': item.get('id', {}).get('S'),
                        'name': item.get('name', {}).get('S'),
                        'cards': cards
                    }
                    lists_with_card.append(list_item)
                    break  # No need to continue checking this list

        return lists_with_card

    except Exception as e:
        raise e
