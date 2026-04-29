.PHONY: help build up down logs shell migrate clean

help:
	@echo "Available commands:"
	@echo "  make build    - Build all containers"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - Show logs"
	@echo "  make shell    - Enter backend shell"
	@echo "  make ps       - Show container status"
	@echo "  make clean    - Clean docker volumes"

build:
	docker-compose build --no-cache

up:
	docker-compose up -d
	docker-compose ps

down:
	docker-compose down

logs:
	docker-compose logs -f

shell:
	docker-compose exec backend /bin/bash

ps:
	docker-compose ps

clean:
	docker-compose down -v
	docker system prune -f

init: build up
	@echo "Waiting for services to be ready..."
	sleep 10
	docker-compose ps
	@echo "Initialization complete!"
	@echo "Access API at: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
