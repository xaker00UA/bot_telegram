FROM python:3.13.3-slim

WORKDIR /app
RUN pip install poetry 
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-root
ADD . .




CMD ["python", "-m", "src.app"]