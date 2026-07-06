import os
import time

import pandas as pd
import psycopg2
import streamlit as st

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mlops")
DB_USER = os.getenv("DB_USER", "mlops")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mlops")

N_MINUTES = 5
REFRESH_SECONDS = 5

st.set_page_config(page_title="ML Operativna Inteligencija", layout="wide")


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


@st.cache_data(ttl=REFRESH_SECONDS)
def load_data() -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM predictions_log ORDER BY ts", conn)
    conn.close()
    return df


st.title("Dashboard za operativnu inteligenciju - praćenje ML modela")

df = load_data()

if df.empty:
    st.info("Još uvek nema podataka. Pokrenite simulator da generišete saobraćaj.")
else:
    df["ts"] = pd.to_datetime(df["ts"])

    cutoff = pd.Timestamp.now() - pd.Timedelta(minutes=N_MINUTES)
    recent_count = int((df["ts"] >= cutoff).sum())

    avg_latency = round(float(df["latency_ms"].mean()), 3)
    total_predictions = len(df)

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Predikcije u poslednjih {N_MINUTES} min", recent_count)
    c2.metric("Prosečna latencija (ms)", avg_latency)
    c3.metric("Ukupno predikcija", total_predictions)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Prosečna latencija (ms) kroz vreme")
        latency_by_minute = (
            df.set_index("ts")["latency_ms"].resample("1min").mean().dropna()
        )
        st.line_chart(latency_by_minute)

    with col2:
        st.subheader("Distribucija predviđenih klasa")
        class_counts = df["prediction"].value_counts()
        st.bar_chart(class_counts)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Distribucija ulaza: MonthlyCharges")
        monthly_bins = pd.cut(df["monthly_charges"], bins=10).value_counts().sort_index()
        monthly_bins.index = monthly_bins.index.astype(str)
        st.bar_chart(monthly_bins)

    with col4:
        st.subheader("Distribucija ulaza: tenure")
        tenure_bins = pd.cut(df["tenure"], bins=10).value_counts().sort_index()
        tenure_bins.index = tenure_bins.index.astype(str)
        st.bar_chart(tenure_bins)

    st.caption(f"Dashboard se osvežava na svakih {REFRESH_SECONDS} sekundi.")

time.sleep(REFRESH_SECONDS)
st.rerun()
