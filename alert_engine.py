import pandas as pd
import os

popular_locations = ["Tokyo", "Bali", "San Francisco", "Jakarta", "Los Angeles", "Kyoto"]

def classify_threat(magnitude, depth):
    if magnitude > 7.0:
        return "🟥 Ekstremalne zagrożenie"
    elif magnitude > 6.0:
        return "🟧 Wysokie zagrożenie"
    elif magnitude > 5.0:
        return "🟨 Umiarkowane zagrożenie"
    else:
        return "🟩 Niskie zagrożenie"

if os.path.exists("filtered_quakes.csv"):
    df = pd.read_csv("filtered_quakes.csv")
else:
    print("Brak pliku z przefiltrowanymi danymi.")
    exit()

if os.path.exists("alerts.csv"):
    alerts_df = pd.read_csv("alerts.csv")
    existing_ids = set(alerts_df["alert_id"])
else:
    alerts_df = pd.DataFrame(columns=["alert_id", "time", "place", "magnitude", "depth", "threat_level", "alert_text"])
    existing_ids = set()

new_alerts = []

for _, row in df.iterrows():
    if any(location in row["place"] for location in popular_locations):
        alert_id = row["id"]
        if alert_id in existing_ids:
            continue

        threat = classify_threat(row["magnitude"], row["depth"])
        alert_text = f"⚠️ ALERT | {row['place']} | {row['magnitude']} M, {row['depth']} km | {threat}"

        new_alerts.append({
            "alert_id": alert_id,
            "time": row["time"],
            "place": row["place"],
            "magnitude": row["magnitude"],
            "depth": row["depth"],
            "threat_level": threat,
            "alert_text": alert_text
        })

        print(alert_text)

if new_alerts:
    new_df = pd.DataFrame(new_alerts)
    alerts_df = pd.concat([alerts_df, new_df], ignore_index=True)
    alerts_df.to_csv("alerts.csv", index=False)
    print(f"\nZapisano {len(new_alerts)} nowych alertów.")
else:
    print("Brak nowych alertów do zapisania.")
