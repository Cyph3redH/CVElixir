from confluent_kafka import Producer
import json
import os
from app.parser.nvd import search_critical_cve

producer = Producer({
    'bootstrap.servers': os.getenv('KAFKA_BROKER', 'kafka:9092'),
})

def publish_nvd():
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