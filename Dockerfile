FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Запускаем Celery Worker + Beat (в одном процессе)
CMD ["celery", "-A", "app.tasks", "worker", "--loglevel=info", "--beat"]