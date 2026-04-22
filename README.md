# CVElixir / Threat Archive — Система мониторинга уязвимостей и угроз

> **CVElixir** — это полностью автономный ETL-пайплайн, который в реальном времени отслеживает появление критических уязвимостей (CVE), новых эксплойтов и опасных новостей в сфере кибербезопасности. Проект создан как **портфолио-работа** и демонстрирует навыки построения **асинхронных, отказоустойчивых и масштабируемых систем** на Python.

## Основные Возможности

- **Автоматический Сбор Данных:** Три независимых парсера мониторят **NVD (CVE)**, **ExploitDB** и **The Hacker News**.

- **Обход Защиты:** Использование **Playwright** и кастомных **User-Agent** для обхода Cloudflare и парсинга динамического контента.

- **Интеллектуальная Дедупликация:** Двухуровневая защита от спама: **Redis** (быстрый кэш, TTL) + **PostgreSQL** (долгосрочное хранение и уникальные индексы).

- **REST API:** Быстрый и легкий API на **FastAPI**, который отдает данные в формате JSON с поддержкой фильтрации (`?source=NVD`).

- **Telegram-Бот:** Мгновенные алерты о новых угрозах прямо в мессенджер.

- **Web-Интерфейс:** Чистый, минималистичный UI на HTML/JS (без Jinja2) для визуализации данных из БД.

- **Продакшен-Готовность:** Полная контейнеризация (**Docker Compose**), обратный прокси (**Nginx**).

# Как запустить проект

1. Создайте своего бота с BotFather и скопируйте его ID

2. Клонируйте репозиторий (bash):

- git clone https://github.com/Cyph3redH/CVElixir.git && cd CVElixir

3. Настройте переменные окружения:

- nano .env

---
    Пример .env:
    TELEGRAM_BOT_TOKEN= токен вашего бота (из BotFather)
    TELEGRAM_CHAT_ID= ваш ID телеграм (узнайте через бота @userinfobot)
    REDIS_PASSWORD= придумайте пароль от Redis
    POSTGRES_USER= укажите имя вашего пользователя в БД PostgreSQL
    POSTGRES_PASSWORD= пароль от вашей БД
    POSTGRES_DB= установите имя БД
    DATABASE_URL= URL вашей БД
---

4. Запустите проект:

- docker compose up -d --build

5. Проверьте работу:

API: http://localhost:8000/
UI: http://localhost:8000/ui
Telegram: Бот отправит алерт при первом же запуске задачи.

## Архитектура Проекта

Проект построен по принципу **Event-Driven Architecture** с использованием очередей.

```mermaid
graph TD
    subgraph "Планировщик (Scheduler)"
        Beat[Celery Beat]
    end

    subgraph "Воркеры (Workers)"
        Worker[Celery Worker]
    end

    subgraph "Парсеры (Parsers)"
        NVD[NVD Parser]
        Exploit[ExploitDB Parser]
        HackerNews[HackerNews Parser]
    end

    subgraph "Хранение (Storage)"
        Redis[(Redis Cache)]
        PostgreSQL[(PostgreSQL DB)]
    end

    subgraph "Публикация (Publishing)"
        API[FastAPI REST]
        Bot[Telegram Bot]
        UI[Web UI / JSON]
    end

    Beat -->|"Каждый час"| Worker
    Worker --> NVD & Exploit & HackerNews
    NVD & Exploit & HackerNews -->|"Сырые данные"| Worker
    Worker -->|"Дедупликация"| Redis
    Worker -->|"Сохранение"| PostgreSQL
    Worker -->|"Алерты"| Bot
    API & UI -->|"Чтение"| PostgreSQL
    User --> Nginx --> API
    User --> Nginx --> UI