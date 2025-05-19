import subprocess
import time

def run_background(path, name=None):
    print(f"\n🚀 Uruchamianie: {path}")
    return subprocess.Popen(["python", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

def run_gui(path):
    print(f"\n🖥️ Uruchamianie GUI aplikacji...")
    return subprocess.Popen(["python", path])

def main():
    print("🌋 TravelQuake – start całego systemu")

    processes = []

    # 1. Producer (USGS → Kafka)
    processes.append(run_background("earthquake_producer.py"))

    # 2. Poczekaj chwilę, żeby Kafka się uruchomiła
    time.sleep(10)

    # 3. Alert Engine (filtered → alerts.csv + Kafka alert_stream)
    processes.append(run_background("alert_engine.py"))

    # 4. Eksport CSV z alertów
    print("\n📁 Generowanie raportu alertów...")
    print("\n⏳ Czekam 10 sekund, aby Kafka była gotowa...")
    time.sleep(60)
    subprocess.run(["python", "csv_exporter.py"])

    # 5. Uruchomienie GUI aplikacji
    run_gui("launcher_gu.py")

    print("\n✅ Wszystkie procesy zostały uruchomione.")
    print("❗ Aby zakończyć – naciśnij Ctrl + C")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Zatrzymywanie procesów...")
        for p in processes:
            p.terminate()

if __name__ == "__main__":
    main()
