from kafka import KafkaProducer
import json
import os
from app.parser.hackernews import fetch_dangerous_articles

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    security_protocol='SASL_PLAINTEXT',
    sasl_mechanism='PLAIN',
    sasl_plain_username='producer',
    sasl_plain_password=os.getenv('KAFKA_PRODUCER_PASSWORD'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_hackernews():
    danger_news = fetch_dangerous_articles
    for news in danger_news:
        event = {
            'source': 'hackersnews',
            'title': news['title'],
            'link': news['link']
        }
        producer.send('raw-security-events', value=event)
    producer.flush()