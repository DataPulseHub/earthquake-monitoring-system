import pandas as pd
import os

# Lista popularnych lokalizacji turystycznych
popular_locations = ["Tokyo", "Bali", "San Francisco", "Jakarta", "Los Angeles", "Kyoto"]

# Funkcja do generowania treści alertów (na podstawie kodu z zadania 3)
def generate_alert_text(place, magnitude, depth):
    if magnitude < 3.0:
        risk_level = "No risk"
        alert_text = f"ALERT: No risk in the region {place}.\n"
    elif 3.0 <= magnitude < 4.0:
        risk_level = "Low risk"
        alert_text = f"EARTHQUAKE ALERT: Earthquake in the region {place}.\n"
    elif 4.0 <= magnitude < 5.0:
        risk_level = "Medium risk"
        alert_text = f"EARTHQUAKE ALERT: Earthquake in the region {place}.\n"
    else:
        risk_level = "High risk"
        alert_text = f"EARTHQUAKE ALERT: Earthquake in the region {place}.\n"

    alert_text += f"Magnitude: {magnitude}, Depth: {depth} km\n"
    alert_text += f"Risk level: {risk_level}\n"

    # Dodatkowe zalecenia
    if magnitude >= 5.0:
        alert_text += "Recommended actions: Evacuation in the affected zones!\n"
    elif magnitude >= 4.0:
        alert_text += "Recommended actions: Exercise caution and monitor the situation.\n"
    else:
        alert_text += "Recommended actions: Monitor the situation, no immediate actions needed.\n"

    return alert_text, risk_level

# Wczytanie danych z filtered_quakes.csv
if os.path.exists("filtered_quakes.csv"):
    df = pd.read_csv("filtered_quakes.csv")
else:
    print("❌ Brak pliku filtered_quakes.csv – nie można wygenerować alertów.")
    exit()

# Sprawdzenie, czy plik alerts.csv już istnieje
if os.path.exists("alerts.csv"):
    alerts_df = pd.read_csv("alerts.csv")
    existing_ids = set(alerts_df["alert_id"])
else:
    alerts_df = pd.DataFrame(columns=[
        "alert_id", "time", "place", "magnitude", "depth", "risk_level", "alert_text"
    ])
    existing_ids = set()

# Przetwarzanie alertów
new_alerts = []

for _, row in df.iterrows():
    if any(location in row["place"] for location in popular_locations):
        alert_id = row["id"]
        if alert_id in existing_ids:
            continue  # unikaj duplikatów

        alert_text, risk_level = generate_alert_text(row["place"], row["magnitude"], row["depth"])

        new_alerts.append({
            "alert_id": alert_id,
            "time": row["time"],
            "place": row["place"],
            "magnitude": row["magnitude"],
            "depth": row["depth"],
            "risk_level": risk_level,
            "alert_text": alert_text
        })

        print(alert_text)

# Zapis do alerts.csv
if new_alerts:
    new_df = pd.DataFrame(new_alerts)
    alerts_df = pd.concat([alerts_df, new_df], ignore_index=True)
    alerts_df.to_csv("alerts.csv", index=False)
    print(f"\n✅ Zapisano {len(new_alerts)} nowych alertów do alerts.csv.")
else:
    print("ℹ️ Brak nowych alertów do zapisania.")
