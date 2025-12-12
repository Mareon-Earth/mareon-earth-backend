.PHONY: dev lint fmt test migrate

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
