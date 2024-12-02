
# Mini Trello Backend

This repository contains the backend implementation for a mini Trello-like application, built using Python Flask and GraphQL with DynamoDB as the database.

## Features

- **GraphQL API**: Provides endpoints to manage boards, lists, and cards.
- **DynamoDB Integration**: Uses AWS DynamoDB as the database for storing and retrieving data.
- **Dockerized Environment**: Easily set up and run the project with Docker Compose.

## Project Structure

```
mini-trello-be/
├── app.py                   # Main Flask application
├── schema.py                # GraphQL schema and resolvers
├── mutations.py             # GraphQL mutations
├── models.py                # Data models for GraphQL types
├── dynamodb_utils.py        # Helper functions for DynamoDB interactions
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image configuration
└── docker-compose.yml       # Docker Compose configuration
```

## Getting Started

### Prerequisites

- **Docker**: Ensure you have Docker and Docker Compose installed on your machine.
- **Python 3.9** (optional if running locally without Docker).

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/haroonfayyaz/mini-trello-be.git
   cd mini-trello-be
   ```

2. Create a `.env` file for environment variables:
   ```bash
   touch .env
   ```

3. Add the necessary environment variables in the `.env` file.

### Running the Project

#### Using Docker

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

2. Access the application at `http://localhost:8080`.

#### Running Locally (Without Docker)

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the Flask server:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```

## GraphQL API

- Access the GraphQL Playground at `http://localhost:8080/graphql`.
- Sample queries and mutations can be found in the `schema.py` and `mutations.py` files.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the MIT License.
