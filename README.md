# Dashboard za operativnu inteligenciju: praćenje ML modela u realnom vremenu

Ovaj projekat predstavlja kontejnerizovan MLOps sistem za praćenje rada jednostavnog modela mašinskog učenja u realnom vremenu. Sistem simulira produkciono okruženje u kojem klijenti šalju zahteve ka predikcionom servisu, a operativne metrike se čuvaju i prikazuju kroz dashboard.

Fokus projekta nije na kompleksnosti samog ML algoritma, već na infrastrukturi oko modela: veb servis, kontejnerizacija, skladištenje operativnih metapodataka, simulacija saobraćaja i vizuelno praćenje ponašanja modela nakon pokretanja.

## Korišćene tehnologije

- **Python** – razvoj API servisa, dashboard-a, trening skripte i simulatora
- **FastAPI** – veb servis za izvršavanje predikcija
- **scikit-learn** – treniranje jednostavnog Logistic Regression modela
- **joblib** – serijalizacija istreniranog modela
- **PostgreSQL** – skladištenje operativnih metapodataka o predikcijama
- **Streamlit** – dashboard za praćenje metrika u realnom vremenu
- **Docker Compose** – orkestracija svih komponenti sistema

## Arhitektura sistema

Sistem se sastoji od četiri povezane komponente:

1. **API servis**  
   FastAPI aplikacija koja učitava prethodno istreniran model iz fajla `model/model.joblib`. API izlaže endpoint `/predict`, prima JSON podatke o korisniku i vraća predikciju da li će korisnik napustiti telekom operatera.

2. **PostgreSQL baza**  
   Baza služi kao skladište operativnih metapodataka. Za svaki zahtev čuvaju se vreme predikcije, ulazni parametri, rezultat predikcije i latencija u milisekundama.

3. **Streamlit dashboard**  
   Dashboard čita podatke iz PostgreSQL baze i prikazuje metrike rada modela: broj predikcija, prosečnu latenciju, distribuciju predviđenih klasa i osnovnu distribuciju ulaznih atributa.

4. **Simulator saobraćaja**  
   Skripta `simulator.py` čita redove iz `data/simulation_stream.csv` i šalje ih kao HTTP POST zahteve ka API servisu. Na taj način se generiše simulirani realan saobraćaj.

## Struktura projekta

```text
ml-ops-dashboard/
├── api/
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── dashboard/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
├── data/
│   ├── Telco-Customer-Churn.csv
│   └── simulation_stream.csv
├── db/
│   └── init.sql
├── model/
│   └── model.joblib
├── simulator/
│   └── Dockerfile
├── training/
│   ├── requirements.txt
│   └── train_model.py
├── .dockerignore
├── .gitignore
├── docker-compose.yml
├── requirements-simulator.txt
├── simulator.py
└── README.md
```

## Dataset i model

Za projekat je korišćen javno dostupan dataset **Telco Customer Churn** sa Kaggle platforme. Cilj modela je binarna klasifikacija korisnika prema tome da li će korisnik napustiti telekomunikacionu uslugu.

Model koristi sledeće atribute:

- `tenure`
- `MonthlyCharges`
- `TotalCharges`
- `SeniorCitizen`

Ciljna promenljiva je:

- `Churn`

Model je jednostavna **Logistic Regression** klasifikacija. Trening se izvršava u odvojenoj skripti `training/train_model.py`, a rezultat treninga se čuva u fajlu `model/model.joblib`.

Važno: model se **ne trenira** prilikom pokretanja API servisa. API samo učitava već serijalizovan model i koristi ga za operativne predikcije.

## Pokretanje sistema

Za pokretanje je potrebno da na računaru bude instaliran Docker Desktop ili Docker Engine sa Docker Compose podrškom.

Sistem se za potrebe odbrane pokreće sa dve komande.

### 1. Pokretanje infrastrukture

```bash
docker compose up --build -d
```

Ova komanda pokreće:

- PostgreSQL bazu
- FastAPI predikcioni servis
- Streamlit dashboard

### 2. Pokretanje simulatora saobraćaja

```bash
docker compose run --rm --build simulator
```

Simulator čita redove iz `data/simulation_stream.csv` i šalje ih ka API servisu na endpoint `/predict`. Nakon pokretanja simulatora, podaci počinju da se upisuju u bazu i prikazuju na dashboard-u.

## Pristup aplikacijama

Nakon pokretanja sistema dostupne su sledeće adrese:

- API dokumentacija: <http://localhost:8000/docs>
- Health check endpoint: <http://localhost:8000/health>
- Streamlit dashboard: <http://localhost:8501>

## Primer zahteva ka API servisu

Endpoint za predikciju je:

```text
POST /predict
```

Primer JSON tela zahteva:

```json
{
  "tenure": 12,
  "MonthlyCharges": 70.5,
  "TotalCharges": 845.2,
  "SeniorCitizen": 0
}
```

Primer odgovora:

```json
{
  "churn_prediction": "No",
  "latency_ms": 2.431
}
```

## Operativne metrike

Prilikom svakog zahteva za predikciju API servis meri latenciju inferencije u milisekundama. Podaci se zatim asinhrono upisuju u PostgreSQL tabelu `predictions_log`.

U bazi se čuvaju:

- vreme izvršavanja predikcije
- ulazni parametri
- kompletan JSON payload
- rezultat predikcije
- latencija predikcije u milisekundama

Streamlit dashboard prikazuje:

- broj predikcija u poslednjih 5 minuta
- prosečnu latenciju predikcionog servisa
- ukupan broj predikcija
- linijski grafikon prosečne latencije kroz vreme
- distribuciju predviđenih klasa
- distribuciju ulaznih atributa `MonthlyCharges` i `tenure`

Ove metrike omogućavaju osnovni operativni nadzor ML servisa nakon pokretanja.

## Ručno treniranje modela

U repozitorijumu su već uključeni `model/model.joblib` i `data/simulation_stream.csv`, tako da ručno treniranje nije potrebno za pokretanje sistema na odbrani.

Ako je potrebno ponovo istrenirati model, komande su:

```bash
pip install -r training/requirements.txt
python training/train_model.py
```

Skripta za trening:

1. učitava `data/Telco-Customer-Churn.csv`,
2. čisti kolonu `TotalCharges`,
3. deli podatke na deo za trening i deo za simulaciju,
4. trenira Logistic Regression model,
5. čuva model u `model/model.joblib`,
6. čuva podatke za simulaciju u `data/simulation_stream.csv`.

## Zaustavljanje sistema

Za zaustavljanje kontejnera koristi se:

```bash
docker compose down
```

Ako je potrebno obrisati i PostgreSQL volume sa starim logovima predikcija:

```bash
docker compose down -v
```

Komanda sa `-v` briše podatke iz baze, pa se pri sledećem pokretanju kreira prazna tabela.

## Napomena

Projekat je namenjen demonstraciji MLOps infrastrukture i operativnog nadzora ML modela. Model je namerno jednostavan, jer je akcenat na arhitekturi sistema, kontejnerizaciji, prikupljanju metrika i prikazu rada servisa u realnom vremenu.
