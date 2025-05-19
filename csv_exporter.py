import json
import pandas as pd
from kafka import KafkaConsumer
import os
import csv

KAFKA_BROKER = "kafka:9092"  # docker-compose: service name
TOPIC = "alert_stream"
CSV_FILE = "data/live_alerts.csv"
os.makedirs("data", exist_ok=True)

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="csv-exporter-group"
)

print("📝 CSV Exporter – nasłuchuje Kafka i zapisuje dane...")

for msg in consumer:
    event = msg.value
    try:
        df = pd.DataFrame([event])
        file_exists = os.path.isfile(CSV_FILE)
        df.to_csv(
            CSV_FILE,
            mode='a',
            index=False,
            header=not file_exists,
            quoting=csv.QUOTE_ALL
        )
        print(f"💾 Zapisano alert: {event.get('alert_id')}")
    except Exception as e:
        print(f"❌ Błąd zapisu do CSV: {e}")
