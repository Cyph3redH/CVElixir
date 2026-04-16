FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Открываем порт для FastAPI (если нужен веб-интерфейс)
EXPOSE 8000

# Запускаем бота (НЕ FastAPI!)
CMD ["python", "-m", "app.bot.alerts"]