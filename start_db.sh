#!/bin/bash
echo "Starting MeetOps Database..."
docker-compose up -d db
if [ $? -ne 0 ]; then
    echo "Error: Failed to start database. Is Docker Desktop running?"
    exit 1
fi
echo "Database started successfully."
echo "You can now run the backend with: cd backend && python -m uvicorn main:app --reload"
