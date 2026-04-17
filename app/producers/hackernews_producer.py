from confluent_kafka import Producer
import json
import os
from app.parser.hackernews import fetch_dangerous_articles

producer = Producer({
    'bootstrap.servers': os.getenv('KAFKA_BROKER', 'kafka:9092'),
    'security.protocol': 'SASL_PLAINTEXT',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': 'producer',
    'sasl.password': os.getenv('KAFKA_PRODUCER_PASSWORD')
})

def publish_hackernews():
    danger_news = fetch_dangerous_articles
    for news in danger_news:
        event = {
            'source': 'hackersnews',
            'title': news['title'],
            'link': news['link']
        }
        producer.produce('raw-security-events', value=json.dumps(event))
    producer.flush()