# API - Payment Project Documentation

## Overview

This project is a robust REST API built with FastAPI, designed to manage authentication, users, API keys, and payment operations. It leverages modern Python best practices and a sophisticated architecture to ensure scalability, security, and maintainability.

**Key Features:**

*   **Authentication:** Secure authentication via JWT (JSON Web Tokens) and API Keys, offering flexible access control.
*   **Rate Limiting:** Implemented using `slowapi` to protect against abuse and ensure fair usage.
*   **Asynchronous Database:** Utilizes Tortoise ORM with an asynchronous PostgreSQL driver (`asyncpg`) for efficient database interactions. SQLite is used for testing.
*   **Comprehensive Logging:** A well-configured logging system provides detailed insights into application behavior, aiding in debugging and monitoring.
*   **Unit Testing:** Extensive unit tests using `pytest` and `httpx` ensure code quality and prevent regressions.
*   **Automatic OpenAPI Documentation:** FastAPI automatically generates OpenAPI documentation, making the API easy to explore and integrate with.

## Project Structure

The project follows a modular structure, promoting code organization and separation of concerns.

```
payment-api/
├── app/
│   ├── api/              # API endpoint definitions
│   │   ├── endpoints/    # Specific API endpoint handlers
│   │   │   ├── apikeys.py  # API key management endpoints
│   │   │   ├── auth.py     # Authentication endpoints (login, registration)
│   │   │   ├── payments.py # Payment-related endpoints
│   │   │   └── users.py    # User management endpoints
│   ├── core/             # Core application logic
│   │   └── auth.py       # Authentication utilities (token creation, verification)
│   ├── services/         # Business logic and data access layers
│   │   └── payment_service.py # Payment-related business logic
│   ├── config.py         # Application configuration using Pydantic Settings
│   ├── dependencies.py   # FastAPI dependency injection definitions
│   ├── logging_config.py # Logging configuration
│   ├── main.py           # Main application entry point (FastAPI instance)
│   ├── models.py         # Tortoise ORM model definitions
│   ├── schemas.py        # Pydantic schemas for request and response validation
│   └── __init__.py       # Makes 'app' a Python package
├── data/              # Data directory
│   └── payments.sql # Sample payment data for database injection
├── tests/             # Unit tests
│   ├── conftest.py    # Pytest configuration and fixtures
│   ├── base.py        # Base test class with common utilities
│   ├── test_apikeys.py# API key endpoint tests
│   ├── test_auth.py   # Authentication endpoint tests
│   ├── test_user.py   # User management endpoint tests
│   └── test_payments.py # Payment endpoint tests
├── .api.config.sample # Sample API configuration file
├── .env.sample        # Sample environment variable file
├── build.sh           # Build script for setup, migration, and Docker image creation
├── entrypoint.sh      # Entrypoint script for Docker containers
├── Dockerfile         # Dockerfile for containerizing the application
├── pyproject.toml     # Poetry project configuration file
├── README.md          # Project README
└── documentation.md   # This documentation file
```

## Initial Setup

This section guides you through setting up the project for development and deployment.

### Prerequisites

*   **Operating System:** Linux (recommended for development and production).  macOS and Windows (with WSL2) are also viable development environments.
*   **Python:** Python 3.12+ is required.  It's highly recommended to use a virtual environment manager like `venv` or `conda`.
*   **PostgreSQL:** PostgreSQL 16+ is recommended for both development and production.  Ensure the PostgreSQL server is running and accessible. SQLite is used for testing.
*   **Poetry (Recommended):** Poetry is a modern Python dependency management tool.  If you don't have it, install it using:

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

### Environment Configuration

1.  **Create a Virtual Environment:**

    ```bash
    python3.12 -m venv .venv  # Create a virtual environment
    source .venv/bin/activate   # Activate the virtual environment
    ```

2.  **Install Dependencies:**

    *   **Using Poetry (Recommended):**

        ```bash
        poetry install
        ```

    *   **Using pip:**

        ```bash
        pip install -r requirements.txt
        ```

3.  **Configure Environment Variables:**

    *   Copy `.env.sample` to `.env`:

        ```bash
        cp .env.sample .env
        ```

    *   Edit `.env` and set the following variables:

        *   `APP_NAME`: The name of your application (e.g., "Payment API").
        *   `APP_DIR`: The application directory (should be "app").
        *   `APP_PORT`: The port the API will listen on (e.g., 8000).
        *   `POSTGRES_USER`: The PostgreSQL username.
        *   `POSTGRES_PASSWORD`: The PostgreSQL password.
        *   `POSTGRES_DB`: The PostgreSQL database name.
        *   `POSTGRES_HOST`: The PostgreSQL host (e.g., "localhost").
        *   `POSTGRES_PORT`: The PostgreSQL port (e.g., 5432).
        *   `BUILD`: Set to `1` to enable the build process.
        *   `PRODUCTION`: Set to `0` for development. Set to `1` for production (Docker image creation).
        *   `INSTALL`: Set to `1` to install dependencies during the build process (if not already installed).
        *   `BUILD_DATABASE`: Set to `1` to create the database, user, and grant privileges.
        *   `INJECT_PAYMENTS`: Set to `1` to inject sample payment data from `data/payments.sql`.
        *   `MIGRATE`: Set to `1` to run database migrations.
        *   `DOCKER_USERNAME`: Your Docker Hub username (if building a Docker image).
        *   `DOCKER_IMAGENAME`: The name of the Docker image.
        *   `DOCKER_IMAGE_TAG`: The tag for the Docker image.

4.  **Configure API Settings:**

    *   Copy `.api.config.sample` to `.api.config`:

        ```bash
        cp .api.config.sample .api.config
        ```

    *   Edit `.api.config` and set the following variables:

        *   `APP_NAME`: The name of your application.
        *   `APP_DIR`: The application directory (should be "app").
        *   `APP_PORT`: The port the API will listen on.
        *   `ALLOWED_HOSTS`: A list of allowed hosts for CORS (e.g., `["localhost", "0.0.0.0", "127.0.0.1"]`).
        *   `DATABASE_URL`: The PostgreSQL connection string (e.g., `postgres://user:password@localhost:5432/payment`).  **Important:** This should match the database credentials in your `.env` file.
        *   `SECRET_KEY`: A strong, randomly generated secret key.  **Critical for security!** Generate one using: `python -c 'import secrets; print(secrets.token_hex(32))'`
        *   `ALGORITHM`: The JWT algorithm (should be "HS256").
        *   `ACCESS_TOKEN_EXPIRE_MINUTES`: The access token expiration time in minutes.
        *   `API_VERSION`: The API version (e.g., "v1").
        *   `API_PREFIX`: The API prefix (e.g., "/api/").

### Database Setup

The `build.sh` script automates database creation and migration.

#### Injecting Sample Payment Data (`INJECT_PAYMENTS`)

If you want to populate the database with sample payment data, create a `data/payments.sql` file containing SQL `INSERT` statements.

**Important Considerations for `payments.sql`:**

*   The `app.models.Payment` model uses a UUID as the primary key (`uuid`).
*   Your `payments.sql` file **must** include a valid UUID for each payment record.
*   **PostgreSQL 13+:** Use the `gen_random_uuid()` function to generate UUIDs if needed.
*   **PostgreSQL < 13:**  You **must** enable the `pgcrypto` extension by running `CREATE EXTENSION pgcrypto;` within your PostgreSQL database before injecting data.

    Example `payments.sql` (PostgreSQL 13+):

    ```sql
    INSERT INTO payments (uuid, date, document, beneficiary, amount) VALUES
    (gen_random_uuid(), NOW(), '12345678901', 'John Doe', 100.00),
    (gen_random_uuid(), NOW(), '98765432109', 'Jane Smith', 250.50);
    ```

### Running the Build Script

1.  **Make the script executable:**

    ```bash
    chmod +x build.sh
    ```

2.  **Execute the script:**

    ```bash
    ./build.sh
    ```

The `build.sh` script will:

*   Install dependencies (if `INSTALL=1`).
*   Create the PostgreSQL database and user (if `BUILD_DATABASE=1`).
*   Grant necessary privileges to the user.
*   Initialize and run database migrations (if `MIGRATE=1`).
*   Inject sample payment data (if `INJECT_PAYMENTS=1`).
*   Build a Docker image (if `PRODUCTION=1`).
*   Output a randomly generated secret key for your `.api.config` file.

## Running the Application

After the initial setup, you can run the application in development mode:

```bash
source .venv/bin/activate # Activate the virtual environment (if not already active)
python run.py
```

This will start the FastAPI development server with hot reloading enabled.  You can access the API at `http://localhost:8000` (or the port specified in your `.env` file).

## Accessing the OpenAPI Documentation

FastAPI automatically generates OpenAPI documentation.  You can access it at:

*   `http://localhost:8000/docs` (Swagger UI)
*   `http://localhost:8000/redoc` (ReDoc)

## Running Tests

To run the unit tests:

```bash
source .venv/bin/activate # Activate the virtual environment (if not already active)
pytest tests/
```

This will execute all tests in the `tests/` directory.

## Dockerization

The project includes a `Dockerfile` for easy containerization.

1.  **Build the Docker image:**

    ```bash
    docker build -t your-docker-username/payment-api .
    ```

    Replace `your-docker-username` with your Docker Hub username.

2.  **Run the Docker container:**

    ```bash
    docker run -p 8080:8080 your-docker-username/payment-api
    ```

    This will run the API in a Docker container, mapping port 8080 on your host machine to port 8080 in the container.

## API Key Generation and Usage

The API supports authentication via API keys.

1.  **Generate an API Key:**

    *   Register a user via the `/api/v1/auth/register` endpoint.
    *   Log in to obtain a JWT token via the `/api/v1/auth/token` endpoint.
    *   Include the JWT token in the `Authorization` header (e.g., `Authorization: Bearer <token>`) when calling the `/api/v1/apikeys/generate` endpoint.  This will generate a new API key for the authenticated user.

2.  **Use the API Key:**

    *   Include the API key in the `X-API-KEY` header or as a query parameter (`api_key`) in your requests.

    Example using the `X-API-KEY` header:

    ```
    curl -H "X-API-KEY: your_api_key" http://localhost:8000/api/v1/payments
    ```

    Example using the `api_key` query parameter:

    ```
    curl http://localhost:8000/api/v1/payments?api_key=your_api_key
    ```

## Logging

The application uses a comprehensive logging system configured in `app/logging_config.py`. Logs are written to both the console and a file (`logs/app.log`).  You can customize the logging level and format in the configuration file.

## Rate Limiting

The API is protected by rate limiting using the `slowapi` library.  The default rate limit is 5 requests per second.  You can adjust the rate limits in the `app/dependencies.py` file.

## Contributing

Contributions to this project are welcome!  Please follow these guidelines:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Write tests for your code.
4.  Submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
