# schema.py

import graphene
from models import *
from mutations import Mutation
from graphql import GraphQLError
from dynamodb_utils import get_cards, get_lists, fetch_card_from_data_store, fetch_lists_with_card
from flask import current_app


class Query(graphene.ObjectType):
    cards = graphene.List(Card)
    card = graphene.Field(Card, id=graphene.ID(required=True))
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

    def resolve_card(self, info, id):
        try:
            card_data = fetch_card_from_data_store(id)
            
            if not card_data:
                raise GraphQLError(f"Card with ID {id} not found")
                
            timestamp = datetime.strptime(
                card_data['timestamp'], "%Y-%m-%dT%H:%M:%S.%fZ"
            ) if card_data.get('timestamp') else None
            
            # Fetch the list name the card is part of
            lists_with_card = fetch_lists_with_card(id)
            current_app.logger.info(f"lists_with_card: {lists_with_card}")
            list = lists_with_card[0] if lists_with_card else None
            
            return Card(
                id=card_data['id'],
                title=card_data['title'],
                description=card_data['description'],
                estimate=card_data['estimate'],
                timestamp=timestamp,
                list=list
            )
        except Exception as e:
            raise GraphQLError(str(e))

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

                lists.append(List(**list_data))

            return lists

        except Exception as e:
            raise GraphQLError(str(e))


schema = graphene.Schema(query=Query, mutation=Mutation)
