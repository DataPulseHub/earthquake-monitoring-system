# earthquake-monitoring-system
System analizy danych sejsmicznych w czasie rzeczywistym.


ZADANIE 3 i 4 (Adam i Ewelina)
Stworzono plik alert_engine.py
Zintegrowano funkcję generującą komunikaty z zadania 3. 
Wczytywane dane z filtered_quakes.csv (którego jeszcze nie mamy, użyłem przykładu)
Filtrowanie po lokalizacjach turystycznych
Klasyfikacja poziomu zagrożenia na podstawie magnitudy
Generowanie alertów tekstowych
Unikanie duplikatów po alert_id
Zapis alertów do alerts.csv
Wyświetlanie alertów w konsoli


## Dashboard:
### Uruchomienie
zainstalowanie zależności:
```shell
pip install -r requierments.txt
```

uruchomienie dashboardu:
```shell
streamlit run .\visualizor.py
```
### Działanie
Dashboard co 1 sekundę zaciąga wartości z pliku csv, domylśnie w kodzie pokazywane jest ostatnie 5 sekund, można zmienić tą 
wartość edytując zmienną globalną: WINDOW_SECONDS
(należy to zmienić, ponieważ zazwyczaj w ostatnich 5 sekundach nie było alertów)

