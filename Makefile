.PHONY: up down logs migrate test reset

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

migrate:
	docker compose exec backend alembic upgrade head

test:
	docker compose run --rm backend pytest -q
	docker compose run --rm frontend npm test -- --run

reset:
	@echo "This removes only this project's database volume."
	docker compose down -v

