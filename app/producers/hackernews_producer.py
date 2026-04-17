from confluent_kafka import Producer
import json
import os
from app.parser.hackernews import fetch_dangerous_articles

def get_producer():
    """Создает и возвращает продюсер Kafka"""
    config = {
        'bootstrap.servers': os.getenv('KAFKA_BROKER', 'host.docker.internal:9092'),
    }
    return Producer(config)

def publish_hackernews():
    producer = get_producer()
    danger_news = fetch_dangerous_articles
    for news in danger_news:
        event = {
            'source': 'hackersnews',
            'title': news['title'],
            'link': news['link']
        }
        producer.produce('raw-security-events', value=json.dumps(event))
    producer.flush()