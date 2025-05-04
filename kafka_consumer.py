from kafka import KafkaConsumer
import json
from datetime import datetime, timedelta
from alert_engine import process_event  # zakładamy, że taka funkcja istnieje


KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'earthquake_data'

def should_alert(event):
    try:
        mag = float(event['magnitude'])
        depth = float(event['depth'])
        time = datetime.utcfromtimestamp(event['time'] / 1000.0)
        return mag > 4.5 and depth < 70 and (datetime.utcnow() - time) < timedelta(minutes=60)
    except:
        return False

consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='alert_filter_group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("📡 Real-time consumer działa – przekazuję dane do alert_engine...")

for msg in consumer:
    event = msg.value
    if should_alert(event):
        process_event(event)
    else:
        print(f"⏭️ Pominięto event: {event['id']} – niespełnione warunki")
