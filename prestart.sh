#!/bin/bash

set -e -x

# Apply database migrations
# alembic upgrade head

echo "Starting the FastAPI application..."
if [ "$DEBUG" = "True" ]; then
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
    uvicorn app.main:app --host 0.0.0.0 --port 8000
fi