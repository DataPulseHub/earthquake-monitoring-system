import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime, timezone

# Config
CSV_PATH = "alerts.csv"
WINDOW_SECONDS = 5

st.set_page_config(page_title="Live Alert Map", layout="wide")
st.title("🗺️ Live Alert Map (last 5 seconds)")

# Refresh every 1000 ms (1 second)
st.experimental_data_editor = None  # prevent legacy warning
st.experimental_rerun = None
st_autorefresh = st.experimental_data_editor or st.experimental_rerun or st.experimental_get_query_params
st_autorefresh = st_autorefresh or st.experimental_rerun

# Use official refresh
st.experimental_data_editor = None
st_autorefresh = st.experimental_rerun or st.experimental_get_query_params
st_autorefresh = st_autorefresh or st.experimental_data_editor
st_autorefresh = st_autorefresh or st.experimental_rerun
st.experimental_rerun = None

# Proper refresh
st_autorefresh = st.experimental_rerun or st.experimental_get_query_params
if st_autorefresh:
    from streamlit.runtime.scriptrunner import add_script_run_ctx
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=1000, key="refresh")

# Load and clean CSV
try:
    df = pd.read_csv(CSV_PATH)

    # Clean lat/lon
    df["longitude"] = df["longitude"].astype(str).str.extract(r"(-?\d+\.\d+)")
    df["latitude"] = df["latitude"].astype(str).str.extract(r"(-?\d+\.\d+)")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")

    # Convert time column
    df["time"] = pd.to_datetime(df["time"], unit='ms', utc=True)
    now = datetime.now(timezone.utc)
    recent_df = df[df["time"] >= now - pd.Timedelta(seconds=WINDOW_SECONDS)]

    if not recent_df.empty:
        # Create map centered on first alert
        first_lat = recent_df.iloc[0]["latitude"]
        first_lon = recent_df.iloc[0]["longitude"]
        m = folium.Map(location=[first_lat, first_lon], zoom_start=6)

        for _, row in recent_df.iterrows():
            popup_text = f"<b>{row['alert_text'].replace(chr(10), '<br>')}</b>"
            color = "red" if str(row['risk_level']).lower() != "no risk" else "green"
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=popup_text,
                icon=folium.Icon(color=color)
            ).add_to(m)

        st_folium(m, width=700, height=500)
    else:
        st.info("No alerts in the last 5 seconds.")

except Exception as e:
    st.error(f"Error reading or processing CSV: {e}")
