from kafka import KafkaProducer
import json
import os
from app.parser.nvd import search_critical_cve

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    security_protocol='SASL_PLAINTEXT',
    sasl_mechanism='PLAIN',
    sasl_plain_username='producer',
    sasl_plain_password=os.getenv('KAFKA_PRODUCER_PASSWORD'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def publish_nvd():
    cves = search_critical_cve()
    for cve in cves:
        event = {
            'source': 'nvd',
            'cve_id': cve['cve_id'],
            'cvss': cve['cvss'],
            'link': cve['link']
        }
        producer.send('raw-security-events', value=event)
    producer.flush()