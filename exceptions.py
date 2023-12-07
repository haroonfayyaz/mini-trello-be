from graphql import GraphQLError


class CardNotFoundError(GraphQLError):
    def __init__(self, id):
        super().__init__(f"Card with ID {id} not found")


class ListNotFoundError(GraphQLError):
    def __init__(self, id):
        super().__init__(f"Card with ID {id} not found")
