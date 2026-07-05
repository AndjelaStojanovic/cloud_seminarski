# ML Ops Dashboard

Ovo je projekat iz predmeta Cloud infrastruktura i servisi. Cilj projekta je da se napravi jednostavan sistem za rad sa modelom mašinskog učenja, gde se model pokreće kroz API servis, a njegove metrike se prate preko dashboard-a.

Projekat koristi dataset Telco Customer Churn. Model predviđa da li će korisnik napustiti uslugu, na osnovu nekoliko ulaznih podataka.

## Kratak opis projekta

Sistem ima četiri glavna dela:

- FastAPI servis koji prima podatke i vraća predikciju
- PostgreSQL bazu u kojoj se čuvaju podaci o svakoj predikciji
- Streamlit dashboard koji prikazuje metrike
- simulator koji šalje više zahteva ka API servisu

Model se ne trenira svaki put kada se pokrene API. Model je prethodno istreniran i sačuvan u fajlu `model/model.joblib`, a API ga samo učitava i koristi za predikcije.

## Korišćene tehnologije

- Python
- FastAPI
- PostgreSQL
- Streamlit
- scikit-learn
- joblib
- Docker
- Docker Compose

## Struktura projekta

```text
ml-ops-dashboard/
├── api/                     # FastAPI aplikacija
├── dashboard/               # Streamlit dashboard
├── data/                    # CSV fajlovi
├── db/                      # SQL skripta za bazu
├── model/                   # Sačuvan model
├── simulator/               # Dockerfile za simulator
├── training/                # Skripta za trening modela
├── docker-compose.yml
├── simulator.py
└── README.md
```

## Dataset i model

Korišćen je Telco Customer Churn dataset. Za model su korišćene sledeće kolone:

- `tenure`
- `MonthlyCharges`
- `TotalCharges`
- `SeniorCitizen`

Ciljna kolona je `Churn`.

Model je Logistic Regression iz biblioteke scikit-learn. Trening modela se nalazi u fajlu `training/train_model.py`. Nakon treninga model se čuva kao `model/model.joblib`.

## Pokretanje projekta

Prva komanda pokreće bazu, API i dashboard:

```bash
docker compose up --build -d
```

Druga komanda pokreće simulator koji šalje zahteve ka API servisu:

```bash
docker compose run --rm --build simulator
```

Nakon pokretanja simulatora, podaci se upisuju u bazu i prikazuju na dashboard-u.

## Linkovi za proveru

API dokumentacija:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

Dashboard:

```text
http://localhost:8501
```

## Primer zahteva

Endpoint za predikciju je `/predict`.

Primer JSON-a koji se šalje API servisu:

```json
{
  "tenure": 12,
  "MonthlyCharges": 70.5,
  "TotalCharges": 845.2,
  "SeniorCitizen": 0
}
```

API vraća predikciju i vreme izvršavanja predikcije u milisekundama.

## Šta se čuva u bazi

Za svaku predikciju u PostgreSQL bazi se čuva:

- vreme predikcije
- ulazni podaci
- rezultat predikcije
- latencija u milisekundama

Dashboard zatim čita podatke iz baze i prikazuje osnovne metrike, kao što su broj predikcija, prosečna latencija i distribucija predviđenih klasa.

## Ponovni trening modela

Za samu proveru projekta ovo nije potrebno, jer su `model/model.joblib` i `data/simulation_stream.csv` već pripremljeni.

Ako je potrebno ponovo istrenirati model, mogu se pokrenuti komande:

```bash
pip install -r training/requirements.txt
python training/train_model.py
```

Skripta učitava dataset iz foldera `data`, trenira model i ponovo pravi fajlove `model/model.joblib` i `data/simulation_stream.csv`.

## Zaustavljanje projekta

Za zaustavljanje kontejnera koristi se:

```bash
docker compose down
```

Ako treba obrisati i podatke iz baze:

```bash
docker compose down -v
```

## Napomena

Model je jednostavan, jer je glavni cilj projekta da se prikaže infrastruktura oko modela: API servis, Docker Compose, baza podataka, simulator saobraćaja i dashboard za praćenje metrika.
