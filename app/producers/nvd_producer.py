from confluent_kafka import Producer
import json
import os
from app.parser.nvd import search_critical_cve

def get_producer():
    """Создает и возвращает продюсер Kafka"""
    config = {
        'bootstrap.servers': os.getenv('KAFKA_BROKER', 'host.docker.internal:9092'),
    }
    return Producer(config)

def publish_nvd():
    producer = get_producer()
    cves = search_critical_cve()
    for cve in cves:
        event = {
            'source': 'nvd',
            'cve_id': cve['cve_id'],
            'cvss': cve['cvss'],
            'link': cve['link']
        }
        producer.produce('raw-security-events', value=json.dumps(event))
    producer.flush()