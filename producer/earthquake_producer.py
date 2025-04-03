import requests
import json
import time
import csv
import os
from datetime import datetime
from kafka import KafkaProducer

# Konfiguracja Kafka
KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'earthquake_data'
CSV_FILE = "data/earthquakes_log.csv"  # Plik do zapisu danych

# Śledzenie ostatnio pobranego timestampu
last_event_time = None

def get_earthquake_data():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['features']
    except Exception as e:
        print(f"[{datetime.now()}] Błąd podczas pobierania danych: {e}")
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

def send_to_kafka(producer, topic, data):
    try:
        producer.send(topic, value=data)
        print(f"[{datetime.now()}] Wysłano do Kafka: {data['id']} - {data['place']}")
    except Exception as e:
        print(f"[{datetime.now()}] Błąd Kafka: {e}")

def load_existing_ids():
    if not os.path.isfile(CSV_FILE):
        return set()
    with open(CSV_FILE, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return set(row['id'] for row in reader)

def save_to_csv(data):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'time', 'place', 'magnitude', 'longitude', 'latitude', 'depth']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def main():
    global last_event_time
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print("⏳ Startuje producent Kafka...")
    print(f"📁 Dane będą zapisywane do: {CSV_FILE}")

    seen_ids = load_existing_ids()

    while True:
        print(f"\n🔄 [{datetime.now()}] Sprawdzam nowe dane...")
        events = get_earthquake_data()
        new_events = []

        for event in events:
            event_info = extract_event_info(event)
            event_time = event_info['time']
            event_id = event_info['id']

            if event_id not in seen_ids:
                new_events.append(event_info)
                seen_ids.add(event_id)

        if new_events:
            new_events.sort(key=lambda x: x['time'])
            for e in new_events:
                send_to_kafka(producer, KAFKA_TOPIC, e)
                save_to_csv(e)
                last_event_time = e['time']
        else:
            print("❌ Brak nowych danych.")

        time.sleep(10)

if __name__ == '__main__':
    main()
