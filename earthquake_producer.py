import requests
import json
import time
import csv
import os
from datetime import datetime
from kafka import KafkaProducer

KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = 'earthquake_data'
CSV_FILE = "earthquakes_log.csv"

def get_earthquake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()['features']
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Błąd pobierania danych: {e}")
        return []

def extract_event_info(event):
    props = event['properties']
    geom = event['geometry']
    return {
        'id': event['id'],
        'time': props['time'],
        'place': props['place'],
        'magnitude': props['mag'],
        'longitude': geom['coordinates'][0],
        'latitude': geom['coordinates'][1],
        'depth': geom['coordinates'][2]
    }

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("⏳ Producent Kafka aktywny...")
    seen_ids = set()

    while True:
        print(f"\n🔄 [{datetime.now()}] Sprawdzanie nowych danych...")
        events = get_earthquake_data()
        print(f"Pobrano {len(events)} zdarzeń.")
        print(events[:1])  # pokazuje 1 przykładowy rekord

        for event in events:
            info = extract_event_info(event)
            if info['id'] not in seen_ids:
                seen_ids.add(info['id'])
                try:
                    producer.send(KAFKA_TOPIC, value=info)
                    print(f"[{datetime.now()}] ✅ Wysłano: {info['id']} - {info['place']}")
                except Exception as e:
                    print(f"❌ Błąd Kafka: {e}")
        time.sleep(60)

if __name__ == '__main__':
    main()
