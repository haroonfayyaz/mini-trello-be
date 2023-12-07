from flask import Flask, jsonify
from flask_graphql import GraphQLView
from schema import schema
import graphene
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)


@app.route('/')
def hello_world():
    return jsonify(message="Hello, World!")


if __name__ == '__main__':
    app.run(debug=True)


# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)
