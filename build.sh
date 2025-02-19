#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
    echo "📂 .env file loaded!"
else
    echo ".env file not found!"
    exit 1
fi

if [[ "$BUILD" -eq 1 ]]; then
    if [[ "$INSTALL" = "1" ]]; then
        echo "🛠️ Building project: "
        echo "╰─ ⏬ Installing requirements"
        poetry export -f requirements.txt --output requirements.txt
        pip install -r requirements.txt
        echo "╰─ ⏬ Installing requirements: ended!"
    fi
    if [ "$BUILD_DATABASE" = "1" ]; then

        echo "Database: $POSTGRES_DB"
        echo "User: $POSTGRES_USER"
        echo "Host: $POSTGRES_HOST"
        echo "Port: $POSTGRES_PORT"

        # Create Database
        create_database() {
            echo "Creating database '$POSTGRES_DB'..."
            psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U postgres -c "CREATE DATABASE $POSTGRES_DB;"
        }

        # Create User
        create_user() {
            echo "Creating user '$POSTGRES_USER' with password '$POSTGRES_PASSWORD'..."
            psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U postgres -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
            psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U postgres -c "ALTER DATABASE $POSTGRES_DB OWNER TO $POSTGRES_USER;"
        }

        # Grant Privileges
        grant_privileges() {
            echo "Granting all privileges on database '$POSTGRES_DB' to user '$POSTGRES_USER'..."
            psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;"
            psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U postgres -c "ALTER USER $POSTGRES_USER CREATEDB;"

            # Conceder privilégios para criar schemas
            psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U postgres -c "GRANT CREATE ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;"

            # Conceder privilégios para excluir tabelas e schemas
            psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U postgres -c "GRANT USAGE, CREATE ON SCHEMA public TO $POSTGRES_USER;"
            psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U postgres -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $POSTGRES_USER;"
        }

        # Execute Functions
        create_database
        create_user
        grant_privileges

        aerich init -t app.config.TORTOISE_ORM --location $APP_DIR/migrations
        aerich init-db

        echo "Database setup completed successfully."
    fi
    if [ "$MIGRATE" = "1" ]; then
        echo "Performing migrations..."
        aerich migrate
        aerich upgrade
        echo "Migrations performed!"
    fi
    if [[ "$INJECT_PAYMENTS" = "1" ]]; then
        psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U postgres -d $POSTGRES_DB -f ./data/payments.sql
    fi
    if [[ "$PRODUCTION" = "1" ]]; then
        echo "🐋 Building Docker image..."
        docker build -t  "$DOCKER_USERNAME"/"$DOCKER_IMAGENAME" .
        echo "🐋 Building Docker image: finished!"
    fi

    chmod +x entrypoint.sh

    echo "🛠️ Building project: ended! "
    echo "🔑 Secret key generated:"
    python -c 'import secrets; print(secrets.token_hex(32))'
else
    echo "Skipping build..."
fi