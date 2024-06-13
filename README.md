# Stonks Backend

## Description
A backend service for managing user profiles, authentication, and real-time chat using WebSockets.

## Requirements
- Python 3.9+
- PostgreSQL
- Firebase
- Google OAuth

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/stonks-backend.git
    cd stonks-backend
    ```

2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Set up the environment variables:
    - Rename `example.env` to `.env`
    - Fill in the required environment variables.

5. Initialize the database:
    ```bash
    flask db upgrade
    ```

6. Run the application:
    ```bash
    flask run
    ```

## Testing WebSocket Functionality
Use the `test_socket.py` script to test WebSocket functionality:
```bash
python test_socket.py
```

## Postman Tests

To test the API endpoints with Postman, follow these steps:

1. Download and install [Postman](https://www.postman.com/downloads/).
2. Clone this repository and navigate to the project directory:
    ```bash
    git clone https://github.com/your-username/stonks-backend.git
    cd stonks-backend
    ```
3. Open Postman and import the collection:
    - Click on the `Import` button in the top left corner.
    - Choose `File` and select the `postman/postman_collection.json` file.
    - The collection will be imported into Postman.

4. Set up environment variables in Postman if necessary:
    - Click on the `Environment` tab in Postman.
    - Create a new environment and add the required variables.

5. Run the requests in the collection to test the API endpoints.
