import streamlit as st
import subprocess
import os
import webbrowser

st.set_page_config(page_title="TravelQuake Launcher", layout="centered")
st.title("🚀 TravelQuake – Launcher GUI")

# Lokalizacja pliku docker-compose.yml
DOCKER_COMPOSE_FILE = "docker-compose.yml"
MAP_URL = "http://localhost:8502"


def run_command(cmd):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding="utf-8", errors="replace")
        output = result.stdout if result.stdout else ""
        errors = result.stderr if result.stderr else ""
        return output + errors
    except Exception as e:
        return f"Błąd uruchamiania: {str(e)}"


if st.button("▶️ Uruchom system (docker-compose up)"):
    with st.spinner("Uruchamianie kontenerów..."):
        output = run_command("docker-compose up -d --build")
        st.code(output)
        st.success("System uruchomiony!")

if st.button("🌐 Otwórz mapę (Streamlit)"):
    with st.spinner("Uruchamianie kontenera mapy..."):
        output = run_command("docker-compose up -d streamlit")
        st.code(output)
    webbrowser.open(MAP_URL, new=2)
    st.success("Mapa uruchomiona i otwarta.")



if st.button("⛔ Zatrzymaj system (docker-compose down)"):
    with st.spinner("Zatrzymywanie kontenerów..."):
        output = run_command("docker-compose down")
        st.code(output)
        st.success("System zatrzymany.")

if st.button("📋 Status kontenerów (docker ps)"):
    output = run_command("docker ps")
    st.code(output)
