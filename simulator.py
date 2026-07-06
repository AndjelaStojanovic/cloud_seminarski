import os
import time

import pandas as pd
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STREAM_PATH = os.path.join(BASE_DIR, "data", "simulation_stream.csv")

API_URL = os.getenv("API_URL", "http://localhost:8000/predict")
HEALTH_URL = os.getenv("HEALTH_URL", API_URL.rsplit("/", 1)[0] + "/health")
SLEEP_SECONDS = float(os.getenv("SLEEP_SECONDS", "1"))

FEATURE_COLUMNS = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]


def wait_for_api(max_attempts: int = 30, pause_seconds: float = 2.0) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(HEALTH_URL, timeout=3)
            if response.status_code == 200:
                print("API je spreman.")
                return
        except requests.RequestException:
            pass

        print(f"Čekam API... pokušaj {attempt}/{max_attempts}")
        time.sleep(pause_seconds)

    raise RuntimeError("API nije dostupan. Proverite da li je docker compose sistem pokrenut.")


def main():
    wait_for_api()

    df = pd.read_csv(STREAM_PATH)
    print(f"Učitano {len(df)} redova iz {STREAM_PATH}")
    print(f"Šaljem zahteve na: {API_URL}")

    for _, row in df.iterrows():
        payload = {col: row[col] for col in FEATURE_COLUMNS}

        try:
            response = requests.post(API_URL, json=payload, timeout=5)
            print(payload, "->", response.status_code, response.json())
        except requests.RequestException as e:
            print(f"Greška prilikom slanja zahteva: {e}")

        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
