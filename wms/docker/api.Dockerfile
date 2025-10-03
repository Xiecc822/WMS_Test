FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md /app/
RUN pip install --upgrade pip && pip install .[dev]

COPY wms /app/wms

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
