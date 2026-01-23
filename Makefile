tests:
	docker compose exec api pytest tests/

coverage:
	docker compose exec api pytest --cov=app tests/

run:
	docker compose up --build