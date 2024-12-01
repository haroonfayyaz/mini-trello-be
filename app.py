from flask import Flask, jsonify
from flask_graphql import GraphQLView
from schema import schema
from flask_cors import CORS
from init_db import initialize_database
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Initialize database tables before the app starts
initialize_database()

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)

@app.route('/')
def hello_world():
    return jsonify(message="Hello, World!")

if __name__ == '__main__':
    app.run(debug=True)
