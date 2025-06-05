FROM python:3.13.3-slim

WORKDIR /app
RUN apt-get update && apt-get install -y redis-server
RUN pip install poetry 
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root
ADD . .




CMD ["sh", "-c", "redis-server --daemonize yes && python -m src.app"]
