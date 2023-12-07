# models.py
import boto3
import graphene
from datetime import datetime
from dynamodb_utils import get_cards
from boto3.dynamodb.conditions import Key, Attr


class Card(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    description = graphene.String()
    timestamp = graphene.DateTime(default_value=datetime.utcnow())
    estimate = graphene.Int()


class List(graphene.ObjectType):
    id = graphene.ID()
    name = graphene.String()
    cards = graphene.List(Card)
    # cards = graphene.Field(graphene.List(Card))
