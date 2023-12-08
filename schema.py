# schema.py

import graphene
from models import *
from mutations import Mutation
from graphql import GraphQLError
from dynamodb_utils import get_cards, get_lists


class Query(graphene.ObjectType):
    cards = graphene.List(Card)
    lists = graphene.List(List)

    def resolve_cards(self, info):
        cards_data = get_cards()

        cards = []
        for data in cards_data:
            timestamp_str = data.get('timestamp', '')
            try:
                timestamp = datetime.strptime(
                    timestamp_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            except ValueError:
                timestamp = None

            card = Card(
                id=data.get('id', ''),
                title=data.get('title', ''),
                description=data.get('description', ''),
                estimate=data.get('estimate', ''),
                timestamp=timestamp
            )
            cards.append(card)

        return cards

    def resolve_lists(root, info):
        try:
            lists_data = get_lists()

            lists = []
            for list_item in lists_data:

                list_data = {
                    'id': list_item.get('id', ''),
                    'name': list_item.get('name', ''),
                    'cards': list_item.get('cards', '')
                }
                print('card is', list_item.get('cards', ''))
                lists.append(List(**list_data))

            return lists

        except Exception as e:
            raise GraphQLError(str(e))


schema = graphene.Schema(query=Query, mutation=Mutation)
