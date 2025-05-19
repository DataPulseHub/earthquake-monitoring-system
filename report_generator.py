import json
import pandas as pd
from kafka import KafkaConsumer
import uuid
import os

# Konfiguracja Kafka
KAFKA_BROKER = "localhost:9092"
TOPIC = "alert_stream"
GROUP_ID = f"report-generator-{uuid.uuid4()}"  # unikalny ID by czytać od początku
OUTPUT_CSV = "data/report_data.csv"
os.makedirs("data", exist_ok=True)

# Połączenie z Kafka
print("📡 Łączenie z Kafka...")
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    consumer_timeout_ms=5000,
    group_id=GROUP_ID
)

# Odbieranie i zapisywanie danych
records = []
print("🔍 Oczekiwanie na wiadomości z Kafka...")
for msg in consumer:
    try:
        alert = msg.value
        alert["time"] = pd.to_datetime(alert["time"], unit="ms", utc=True)
        records.append(alert)
        print(f"✅ Odebrano alert: {alert.get('alert_id', 'brak ID')} – {alert.get('place')}")
    except Exception as e:
        print(f"❌ Błąd: {e}")

if records:
    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"💾 Dane zapisane do: {OUTPUT_CSV}")
else:
    print("⚠️ Brak danych – plik CSV nie został wygenerowany.")
