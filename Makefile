.PHONY: dev lint test revision upgrade seed

dev:
uvicorn app.main:app --reload

lint:
ruff check .
black --check .

test:
pytest -q

revision:
alembic -c wms/alembic.ini revision --autogenerate -m "manual"

upgrade:
alembic -c wms/alembic.ini upgrade head

seed:
python wms/scripts/seed.py
