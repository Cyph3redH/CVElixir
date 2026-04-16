from celery import Celery
from celery.schedules import crontab
import os

REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

# Создаём Celery приложение
app = Celery(
    'cvelixir',
    broker=f'redis://{REDIS_PASSWORD}redis:6379/0',
    backend=f'redis://{REDIS_PASSWORD}redis:6379/0'
)

# Настройка расписания
app.conf.beat_schedule = {
    'check-every-hour': {
        'task': 'app.tasks.check_all_sources',
        'schedule': crontab(minute=0),  # Каждый час в :00
    },
}
app.conf.timezone = 'UTC'