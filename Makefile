.PHONY: dev lint fmt test migrate db-up db-down db-rebuild

dev:
	./scripts/run.sh

lint:
	./scripts/lint.sh

fmt:
	./scripts/format.sh

test:
	./scripts/test.sh

migrate:
	./scripts/migrate.sh

db-up:
	docker-compose up -d db

db-down:
	docker-compose down

db-rebuild:
	@echo "Rebuilding database... This will delete all local data."
	docker-compose down -v
	docker-compose up -d db
