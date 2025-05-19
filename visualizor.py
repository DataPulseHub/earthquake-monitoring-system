import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from datetime import datetime, timezone, timedelta
from kafka import KafkaConsumer
import json
from streamlit_autorefresh import st_autorefresh

# Konfiguracja
KAFKA_TOPIC = "alert_stream"
KAFKA_BROKER = "kafka:9092"
REFRESH_INTERVAL_MS = 5000
RECORD_LIMIT = 100

# Ustawienia Streamlit
st.set_page_config(page_title="TravelQuake – Alert Map", layout="wide")
st.title("🌍 TravelQuake – Live Alert Map (last 24 hours)")
st_autorefresh(interval=REFRESH_INTERVAL_MS, key="auto-refresh")

# Styl mapy
tile_options = {
    "🗺️ Klasyczna": "OpenStreetMap",
    "🧼 Minimalistyczna": "CartoDB positron",
    "🌄 Terenowa": "Stamen Terrain"
}
tile_name = tile_options[st.selectbox("Styl mapy:", list(tile_options.keys()))]
default_lat, default_lon = 39.8283, -98.5795  # USA środek

# Bufor alertów
if "history" not in st.session_state:
    st.session_state["history"] = []

try:
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id="streamlit-map-group",
        consumer_timeout_ms=5000
    )

    messages = consumer.poll(timeout_ms=5000, max_records=RECORD_LIMIT)
    now = datetime.now(timezone.utc)

    for tp, msgs in messages.items():
        for msg in msgs:
            e = msg.value
            if all(k in e for k in ["latitude", "longitude", "time"]):
                try:
                    e["time"] = pd.to_datetime(e["time"], unit="ms", utc=True)
                    e["latitude"] = float(e["latitude"])
                    e["longitude"] = float(e["longitude"])
                    st.session_state["history"].append(e)
                except:
                    continue

    # ❗ Tymczasowe wyłączenie filtra czasu (do debugowania)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
    data = [e for e in st.session_state["history"] if e["time"] >= cutoff]
    st.info(f"📊 Liczba wszystkich alertów: {len(data)}")

    # Podgląd 5 ostatnich
    for i, e in enumerate(data[-5:]):
        st.text(f"{i+1}. {e['place']} | {e['risk_level']} | {e['time']}")

    # Mapowanie
    if data:
        df = pd.DataFrame(data).dropna(subset=["latitude", "longitude"])
        first_lat = df.iloc[0]["latitude"]
        first_lon = df.iloc[0]["longitude"]
        m = folium.Map(location=[first_lat, first_lon], zoom_start=2, tiles=tile_name)
        cluster = MarkerCluster().add_to(m)

        for _, row in df.iterrows():
            risk = row["risk_level"].lower()
            if risk in ["no risk", "low"]:
                color = "green"
            elif risk == "moderate":
                color = "orange"
            elif risk in ["high", "extreme"]:
                color = "red"
            else:
                color = "blue"
        
            popup_html = f"""
            <div style='width: 250px; font-family: Arial, sans-serif;'>
              <h4 style='margin: 0; color: #333;'>{row['risk_level'].upper()} RISK</h4>
              <hr style='margin:4px 0;'>
              <p style='margin: 4px 0;'><b>📌 Location:</b> {row['place']}</p>
              <p style='margin: 4px 0;'><b>📈 Magnitude:</b> {row['magnitude']}</p>
              <p style='margin: 4px 0;'><b>🔎 Depth:</b> {row['depth']} km</p>
              <p style='margin: 4px 0;'><b>⏰ Time:</b> {row['time'].strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            """
        
            emoji = {
                "no risk": "🟢",
                "low": "🟡",
                "moderate": "🟠",
                "high": "🔴",
                "extreme": "☠"
            }.get(risk, "❓")
        
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=popup_html,
                icon=folium.DivIcon(html=f"<div style='font-size:24px;'>{emoji}</div>")
            ).add_to(cluster)


    else:
        m = folium.Map(location=[default_lat, default_lon], zoom_start=2, tiles=tile_name)
        st.info("Brak alertów do wyświetlenia.")

except Exception as e:
    st.error("❌ Błąd połączenia z Kafka lub przetwarzania danych.")
    st.exception(e)

# Wyświetlenie mapy
st_folium(m, width="100%", height=700)
