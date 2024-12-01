import os
from dotenv import load_dotenv

load_dotenv()

# models.py

import boto3
import graphene
from models import Card, List
from datetime import datetime
from graphql import GraphQLError
from exceptions import CardNotFoundError, ListNotFoundError
from dynamodb_utils import fetch_card_from_data_store, fetch_lists_with_card

dynamodb = boto3.client('dynamodb', endpoint_url=os.getenv('DYNAMODB_ENDPOINT_URL'))


def get_card_by_id(id):
    response = dynamodb.get_item(
        TableName='Cards',
        Key={
            'id': {'S': id}
        }
    )

    if 'Item' not in response:
        raise CardNotFoundError(id)

    return response['Item']


def get_list_by_id(id):
    response = dynamodb.get_item(
        TableName='BoardList',
        Key={
            'id': {'S': id}
        }
    )

    if 'Item' not in response:
        raise CardNotFoundError(id)

    return response['Item']


def fetch_list_from_data_store(list_id):

    response = dynamodb.get_item(
        TableName='BoardList',
        Key={'id': {'S': list_id}}
    )

    item = response.get('Item')

    if item:
        return {
            'id': item.get('id').get('S'),
            'name': item.get('name').get('S'),
            'cards': item.get('cards').get('L') or []
        }
    else:
        return None

def save_list_to_data_store(list_item):
    try:

        item = {
            'id': {'S': list_item['id']},
            'name': {'S': list_item['name']},
            'cards': {'L': list_item['cards'] or []}
        }
        response = dynamodb.put_item(
            TableName='BoardList',
            Item=item
        )

        if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
            return True
        else:
            raise Exception("Failed to save list")

    except Exception as e:
        raise e

class CreateCard(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String()
        estimate = graphene.Int()

    card = graphene.Field(Card)

    def mutate(self, info, title, description='', estimate=0):
        try:
            timestamp = datetime.utcnow()
            id = str(int(timestamp.timestamp()))

            response = dynamodb.put_item(
                TableName='Cards',
                Item={
                    'id': {'S': id},
                    'title': {'S': title},
                    'description': {'S': description},
                    'estimate': {'N': str(estimate)},
                    'timestamp': {'S': timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
                }
            )

            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                return CreateCard(card=Card(
                    id=id,
                    title=title,
                    description=description,
                    timestamp=timestamp,
                    estimate=estimate,
                ))

            raise Exception("Failed to create card")

        except Exception as e:
            raise GraphQLError(str(e))


class DeleteCard(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:
            card_data = get_card_by_id(id)

            response = dynamodb.delete_item(
                TableName='Cards',
                Key={
                    'id': {'S': id}
                }
            )

            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                lists_with_card = fetch_lists_with_card(id)
                for list_item in lists_with_card:
                    if 'cards' in list_item:
                        cards_list = list_item['cards']
                        for i, card_obj in enumerate(cards_list):
                            if card_obj['M']['id']['S'] == id:
                                cards_list.pop(i)
                                save_list_to_data_store(list_item)

                return DeleteCard(success=True)

            raise Exception("Failed to delete card")

        except CardNotFoundError as e:
            raise GraphQLError(str(e))

        except Exception as e:
            raise GraphQLError(str(e))


class UpdateCard(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        title = graphene.String()
        description = graphene.String()
        estimate = graphene.Int()

    success = graphene.Boolean()

    def mutate(self, info, id, **kwargs):
        try:
            get_card_by_id(id)

            update_expression = []
            expression_attribute_names = {}
            expression_attribute_values = {}

            for key, value in kwargs.items():
                if value is not None:
                    update_expression.append(f"#{key} = :{key}")
                    expression_attribute_names[f'#{key}'] = key
                    if isinstance(value, int):
                        expression_attribute_values[f':{key}'] = {'N': str(value)}
                    else:
                        expression_attribute_values[f':{key}'] = {'S': value}

            if not update_expression:
                raise Exception("No valid attributes provided for update")

            response = dynamodb.update_item(
                TableName='Cards',
                Key={
                    'id': {'S': id}
                },
                UpdateExpression='SET ' + ', '.join(update_expression),
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values
            )

            return UpdateCard(success=True)

        except CardNotFoundError as e:
            raise GraphQLError(str(e))

        except Exception as e:
            raise GraphQLError(str(e))


class CreateList(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)

    list = graphene.Field(List)

    def mutate(self, info, name):
        try:
            timestamp = datetime.utcnow()
            id = str(int(timestamp.timestamp()))

            response = dynamodb.put_item(
                TableName='BoardList',
                Item={
                    'id': {'S': id},
                    'name': {'S': name},
                    # Initialize with an empty list of cards
                    'cards': {'L': []}
                }
            )

            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                return CreateList(list=List(
                    id=id,
                    name=name,
                    cards=[]
                ))
            else:
                raise Exception("Failed to create list")

        except Exception as e:
            raise GraphQLError(str(e))


class AddCardToList(graphene.Mutation):
    class Arguments:
        list_id = graphene.ID(required=True)
        card_id = graphene.ID(required=True)

    list = graphene.Field(List)

    def mutate(self, info, list_id, card_id):
        try:
            list_item = fetch_list_from_data_store(list_id)

            if list_item:
                existing_card = fetch_card_from_data_store(card_id)

                if existing_card:

                    card_ids = [card['M']['id']['S']
                                for card in list_item.get('cards', [])]

                    if card_id in card_ids:
                        raise Exception("Card already exists in the list")

                    card_item = {
                        "M": {
                            "id": {"S": existing_card['id']},
                            "title": {"S": existing_card['title']},
                            "description": {"S": existing_card['description']},
                            "estimate": {"N": str(existing_card['estimate'])},
                            "timestamp": {"S": existing_card['timestamp']}
                        }
                    }

                    list_item['cards'].append(card_item)

                    save_list_to_data_store(list_item)

                    return AddCardToList(list=list_item)
                else:
                    raise Exception("Existing card not found")
            else:
                raise Exception("List not found")

        except Exception as e:
            raise Exception(str(e))


# class RemoveCardFromList(graphene.Mutation):
#     class Arguments:
#         list_id = graphene.ID(required=True)
#         card_id = graphene.ID(required=True)

#     list = graphene.Field(List)

#     def mutate(self, info, list_id, card_id):
#         try:

#             list_item = fetch_list_from_data_store(list_id)

#             if list_item:

#                 cards_list = list_item.get('cards', [])

#                 for i, card_obj in enumerate(cards_list):
#                     if card_obj['M']['id']['S'] == card_id:
#                         # Remove the card from the list
#                         removed_card = cards_list.pop(i)

#                         save_list_to_data_store(list_item)

#                         return RemoveCardFromList(list=list_item)

#                 raise Exception("Card not found in the list")

#             else:
#                 raise Exception("List not found")

#         except Exception as e:
#             raise Exception(str(e))

class ManageCardInList(graphene.Mutation):
    class Arguments:
        source_list_id = graphene.ID(required=True)
        destination_list_id = graphene.ID()
        card_id = graphene.ID(required=True)

    source_list = graphene.Field(List)
    destination_list = graphene.Field(List)

    def mutate(self, info, source_list_id, card_id, destination_list_id=None):
        try:

            source_list_item = fetch_list_from_data_store(source_list_id)

            if source_list_item:
                if destination_list_id:

                    destination_list_item = fetch_list_from_data_store(
                        destination_list_id)
                    if destination_list_item:

                        source_cards_list = source_list_item.get('cards', [])
                        for i, card_obj in enumerate(source_cards_list):
                            if card_obj['M']['id']['S'] == card_id:
                                removed_card = source_cards_list.pop(i)
                                break
                        else:
                            raise Exception(
                                "Card not found in the source list")

                        destination_cards_list = destination_list_item.get(
                            'cards', [])
                        card_exists = False
                        for card_obj in destination_cards_list:
                            if card_obj['M']['id']['S'] == card_id:
                                card_exists = True
                                break

                        if not card_exists:

                            card_item = {
                                "M": {
                                    "id": {"S": removed_card['M']['id']['S']},
                                    "title": {"S": removed_card['M']['title']['S']},
                                    "description": {"S": removed_card['M']['description']['S']},
                                    "estimate": {"N": removed_card['M']['estimate']['N']},
                                    "timestamp": {'S': removed_card['M']['timestamp']['S']}
                                }
                            }
                            destination_cards_list.append(card_item)

                            save_list_to_data_store(source_list_item)
                            save_list_to_data_store(destination_list_item)

                        return ManageCardInList(source_list=source_list_item, destination_list=destination_list_item)
                    else:
                        raise Exception("Destination list not found")
                else:

                    source_cards_list = source_list_item.get('cards', [])
                    for i, card_obj in enumerate(source_cards_list):
                        if card_obj['M']['id']['S'] == card_id:
                            removed_card = source_cards_list.pop(i)
                            break
                    else:
                        raise Exception("Card not found in the source list")

                    save_list_to_data_store(source_list_item)

                    return ManageCardInList(source_list=source_list_item, destination_list=None)
            else:
                raise Exception("Source list not found")

        except Exception as e:
            raise Exception(str(e))


class DeleteList(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        try:

            get_list_by_id(id)

            response = dynamodb.delete_item(
                TableName='BoardList',
                Key={
                    'id': {'S': id}
                }
            )

            if response.get('ResponseMetadata', {}).get('HTTPStatusCode') == 200:
                return DeleteList(success=True)

            raise Exception("Failed to delete list")

        except ListNotFoundError as e:
            raise GraphQLError(str(e))

        except Exception as e:
            raise GraphQLError(str(e))


class UpdateListName(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id, name):
        try:

            get_list_by_id(id)

            response = dynamodb.update_item(
                TableName='BoardList',
                Key={
                    'id': {'S': id}
                },
                UpdateExpression='SET #name = :name',
                ExpressionAttributeNames={
                    '#name': 'name'
                },
                ExpressionAttributeValues={
                    ':name': {'S': name}
                }
            )

            return UpdateListName(success=True)

        except ListNotFoundError as e:
            raise GraphQLError(str(e))

        except Exception as e:
            raise GraphQLError(str(e))


class Mutation(graphene.ObjectType):
    create_card = CreateCard.Field()
    update_card = UpdateCard.Field()
    delete_card = DeleteCard.Field()
    create_list = CreateList.Field()
    delete_list = DeleteList.Field()
    update_list = UpdateListName.Field()
    add_card_to_list = AddCardToList.Field()
    # remove_card_from_list = RemoveCardFromList.Field()
    manage_card_in_list = ManageCardInList.Field()
