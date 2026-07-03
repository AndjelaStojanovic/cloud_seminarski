# Dashboard za operativnu inteligenciju - praćenje ML modela u realnom vremenu

Kontejnerizovan MLOps demo sistem sa četiri komponente:

1. **API servis** (FastAPI) - učitava istreniran `model.joblib` i vraća predikcije preko `/predict`, uz merenje latencije.
2. **Baza podataka** (PostgreSQL) - skladišti vreme, ulazne parametre, predikciju i latenciju svake predikcije.
3. **Dashboard** (Streamlit) - prikazuje operativne metrike i osnovnu distribuciju ulaznih podataka.
4. **Simulator saobraćaja** - šalje redove iz CSV fajla ka API servisu i generiše realan saobraćaj.

Model je jednostavna **Logistic Regression** iz biblioteke `scikit-learn`, trenirana nad datasetom **Telco Customer Churn** sa Kaggle platforme.

## Struktura projekta

```text
ml-ops-dashboard/
├── api/                         # FastAPI predikcioni servis
├── dashboard/                   # Streamlit dashboard
├── data/                        # CSV dataset i stream za simulaciju
├── db/init.sql                  # Inicijalizacija PostgreSQL tabele
├── model/model.joblib           # Serijalizovan istreniran model
├── simulator/Dockerfile         # Docker image za simulator
├── simulator.py                 # Skripta koja generiše zahteve ka API-ju
├── training/train_model.py      # Jednokratni trening modela
├── docker-compose.yml           # Orkestracija svih servisa
└── README.md
```

## Priprema dataset-a i modela

U ovom repozitorijumu može da stoji manji razvojni CSV samo za testiranje strukture. Za finalnu predaju preuzeti pravi Kaggle dataset:

- Kaggle: `Telco Customer Churn`
- Očekivan fajl: `Telco-Customer-Churn.csv`
- Ciljna kolona: `Churn`
- Atributi koje ovaj projekat koristi: `tenure`, `MonthlyCharges`, `TotalCharges`, `SeniorCitizen`

Zameniti fajl:

```text
data/Telco-Customer-Churn.csv
```

Zatim jednom istrenirati model:

```bash
pip install -r training/requirements.txt
python training/train_model.py
```

Ova komanda generiše:

```text
model/model.joblib
data/simulation_stream.csv
```

Za odbranu rada oba fajla mogu biti već prisutna u repozitorijumu, kako asistent ne bi morao da trenira model ručno.

## Pokretanje sistema za odbranu

Nakon što su `model/model.joblib` i `data/simulation_stream.csv` već pripremljeni, sistem se podiže i testira sa dve komande:

```bash
docker compose up --build -d
```

```bash
docker compose run --rm simulator
```

Otvoriti:

- API dokumentacija: http://localhost:8000/docs
- Dashboard: http://localhost:8501

## Primer JSON zahteva

```json
{
  "tenure": 12,
  "MonthlyCharges": 70.5,
  "TotalCharges": 845.2,
  "SeniorCitizen": 0
}
```

## Zaustavljanje sistema

```bash
docker compose down -v
```

`-v` briše i PostgreSQL volume, pa se time čiste stari logovi predikcija.
