FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md /app/
RUN pip install --upgrade pip && pip install .[dev]

COPY wms /app/wms

CMD ["celery", "-A", "app.tasks.celery_app:celery_app", "worker", "-l", "info"]
