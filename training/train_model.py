import os

import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "Telco-Customer-Churn.csv")
SIMULATION_STREAM_PATH = os.path.join(BASE_DIR, "data", "simulation_stream.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")

FEATURE_COLUMNS = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]
TARGET_COLUMN = "Churn"

TRAIN_FRACTION = 0.3  # 30% za trening, 70% za simulaciju saobraćaja


def load_and_clean_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(0)

    df = df.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN])
    return df


def main():
    print(f"Učitavam podatke iz: {DATA_PATH}")
    df = load_and_clean_data(DATA_PATH)

    # Podela na deo za trening i deo za simulaciju saobraćaja
    train_df, stream_df = train_test_split(
        df, train_size=TRAIN_FRACTION, random_state=42, stratify=df[TARGET_COLUMN]
    )

    os.makedirs(os.path.dirname(SIMULATION_STREAM_PATH), exist_ok=True)
    stream_df.to_csv(SIMULATION_STREAM_PATH, index=False)
    print(f"Sačuvano {len(stream_df)} redova za simulaciju saobraćaja: {SIMULATION_STREAM_PATH}")

    X_train = train_df[FEATURE_COLUMNS]
    y_train = (train_df[TARGET_COLUMN] == "Yes").astype(int)

    print(f"Treniram model na {len(train_df)} redova...")
    model = Pipeline(steps=[
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=1000)),
    ])
    model.fit(X_train, y_train)

    train_accuracy = model.score(X_train, y_train)
    print(f"Tačnost na trening skupu: {train_accuracy:.3f}")

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model sačuvan: {MODEL_PATH}")


if __name__ == "__main__":
    main()
