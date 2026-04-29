#!/bin/bash
echo "Starting deployment..."

cd backend
docker-compose up -d --build

sleep 10
docker-compose exec backend python scripts/init_db.py

echo "Deployment completed!"
