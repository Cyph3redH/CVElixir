from celery import Celery
from celery.schedules import crontab

# Создаём Celery приложение
app = Celery(
    'cvelixir',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

# Настройка расписания
app.conf.beat_schedule = {
    'check-every-hour': {
        'task': 'app.tasks.check_all_sources',
        'schedule': crontab(minute=0),  # Каждый час в :00
    },
}
app.conf.timezone = 'UTC'