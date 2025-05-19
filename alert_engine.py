import json
from kafka import KafkaProducer, KafkaConsumer
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ————— KONFIGURACJA —————
KAFKA_BROKER = "kafka:9092"
SOURCE_TOPIC = "earthquake_data"
ALERT_TOPIC  = "alert_stream"

# dane do SMTP
FROM_EMAIL    = "travelquake.alerts@gmail.com"          # Gmail
FROM_PASSWORD = "dgdb cffe ynsz vksu"   # Hasło aplikacji

# ————— PRODUCER i CONSUMER —————
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

consumer = KafkaConsumer(
    SOURCE_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="alert-engine-group"
)

# ————— FUNKCJE POMOCNICZE —————
def load_emails_from_csv(path="emails.csv"):
    try:
        df = pd.read_csv(path, header=None, names=["email"])
        return df["email"].dropna().tolist()
    except Exception as e:
        print(f"❌ Błąd wczytywania pliku emails.csv: {e}")
        return []

def send_email_alert(subject, body, to_emails):
    for to_email in to_emails:
        msg = MIMEMultipart()
        msg["From"]    = FROM_EMAIL
        msg["To"]      = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(FROM_EMAIL, FROM_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"📧 Wysłano powiadomienie do: {to_email}")
        except Exception as e:
            print(f"❌ Błąd wysyłania do {to_email}: {e}")

# ————— START —————
print("🚨 Alert Engine – nasłuchiwanie zdarzeń...")

emails_list = load_emails_from_csv("emails.csv")
if not emails_list:
    print("⚠️ Brak adresów w emails.csv – powiadomienia e-mail wyłączone.")

for msg in consumer:
    try:
        row = msg.value
        # walidacja pól
        if not all(k in row for k in ["id","place","time","latitude","longitude","magnitude","depth"]):
            print("⚠️ Pominięto: brak wymaganych pól.")
            continue

        # parsowanie czasu
        parsed_time = pd.to_datetime(int(row["time"]), unit="ms", utc=True)
        if parsed_time.year < 2000:
            print(f"⚠️ Pominięto: niepoprawna data {row['time']}")
            continue

        # poziom ryzyka
        risk_level = (
            "Extreme" if row["magnitude"] >= 7 else
            "High"    if row["magnitude"] >= 6 else
            "Moderate"if row["magnitude"] >= 5 else
            "Low"     if row["magnitude"] >= 4 else
            "No risk"
        )

        # budowa alertu
        alert = {
            "alert_id":  row["id"],
            "place":     row["place"],
            "time":      int(parsed_time.timestamp()*1000),
            "latitude":  float(row["latitude"]),
            "longitude": float(row["longitude"]),
            "magnitude": float(row["magnitude"]),
            "depth":     row["depth"],
            "risk_level":risk_level,
            "alert_text":f"{risk_level} risk in {row['place']}."
        }

        # wysyłka do Kafka
        producer.send(ALERT_TOPIC, alert)
        print(f"📤 Wysłano alert: {alert['alert_id']} | {alert['place']} | {alert['risk_level']}")

        # powiadomienie e-mail, jeśli moderate+
        if risk_level in ["Moderate","High","Extreme"] and emails_list:
            subject = f"TravelQuake ALERT: {risk_level} risk in {row['place']}"
            body = (
                f"Alert details:\n"
                f"Place: {row['place']}\n"
                f"Time: {parsed_time}\n"
                f"Magnitude: {row['magnitude']}\n"
                f"Depth: {row['depth']} km\n"
                f"Risk Level: {risk_level}\n"
                f"Alert Text: {alert['alert_text']}"
            )
            send_email_alert(subject, body, emails_list)

    except Exception as e:
        print(f"❌ Błąd przetwarzania alertu: {e}")
