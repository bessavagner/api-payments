#!/bin/bash

source .venv/bin/activate

# Load environment variables from .env file
if [ -f .env ]; then
  export $(cat .env | grep -v '#' | awk '/=/ {print $1}')
else
  echo ".env file not found!"
  exit 1
fi

if [ "$BUILD" = "1" ]; then
  if [ "$MIGRATE" = "1" ]; then
    aerich migrate
    aerich upgrade
  fi
fi
if [ "$PRODUCTION" = "1" ]; then
  echo "⛔ Production server not implemented yet!"
  # gunicorn --bind "0.0.0.0:$APP_PORT" "$APP_NAME.asgi" --log-level info --chdir $APP_NAME -w 4 --worker-connections=1000 --threads 2 -k uvicorn.workers.UvicornWorker
else
  echo "⚠️ Using unsecure debug server."
  python run.py  # programmatically uvicorn server
fi