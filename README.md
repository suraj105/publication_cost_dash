
# Dashboard zur Analyse der Publikationskosten

Ein interaktives Dashboard auf Basis von Dash (Plotly), das wissenschaftliche Publikationskosten mithilfe von angereicherten Daten aus **PubMed**, **OpenAPC** und **DOAJ** visualisiert.

---

## Funktionen

- Filterung nach **Jahr**, **Land** und **Journal**
- Visualisierungen:
  - Durchschnittliche Publikationskosten pro Jahr
  - Verteilung der Match-Quellen (DOI, ISSN, manuell, unmatched)
  - Top 10 der häufigsten nicht gematchten ISSNs
  - (Geplant) Top 10 der teuersten Journale
- Manuelle Preisangabe für nicht zugeordnete Einträge
- Export des Datensatzes als CSV-Datei

---

## Voraussetzungen

- Python `3.11+`
- PostgreSQL `13+`

---

## nstallation

### 1. Repository klonen

```bash
git clone https://github.com/suraj105/publication_cost_dash.git
cd publication_cost_dash
```

### 2. Virtuelle Umgebung erstellen

```bash
python3 -m venv .venv
source .venv/bin/activate      # für macOS/Linux
# oder
.venv\Scripts\activate         # für Windows
```

### 3. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

#### `requirements.txt`

```txt
dash==3.1.1
plotly==6.2.0
pandas==2.3.1
tqdm==4.67.1
SQLAlchemy==2.0.42
psycopg2-binary==2.9.10
Flask==3.1.1
Werkzeug==3.1.3
Jinja2==3.1.6
python-dateutil==2.9.0.post0
pytz==2025.2
tzdata==2025.2
```

---

## 🛠️ PostgreSQL einrichten

### 1. PostgreSQL installieren  
[https://www.postgresql.org/download/](https://www.postgresql.org/download/)

### 2. Datenbank & Benutzer anlegen

```sql
CREATE DATABASE dashdb;
CREATE USER dashuser WITH PASSWORD 'dein_passwort';
GRANT ALL PRIVILEGES ON DATABASE dashdb TO dashuser;
```

### 3. Datenbankzugang konfigurieren

Bearbeite `db/db_config.py`:

```python
DB_NAME = "dashdb"
DB_USER = "dashuser"
DB_PASSWORD = "dein_passwort"
DB_HOST = "localhost"
DB_PORT = "5432"
```

---

## ▶️ Dashboard starten

```bash
python app.py
```

Du wirst gefragt:

- **Sind die Daten bereits geladen?** → `y` oder `n` 
- **Wurde die Enrichment durchgeführt?** → `y` oder `n`

Danach öffnet sich das Dashboard unter  
[http://localhost:8050](http://localhost:8050)

---

## 📁 Projektstruktur

```
.
├── app.py                      # Einstiegspunkt für das Dash-App
├── dash_main.py                # Startlogik & Layoutbindung
├── dash_components/
│   ├── layout.py               # Benutzeroberfläche (HTML, Dropdowns etc.)
│   └── callback.py             # Interaktive Logik & Updates
├── db/
│   ├── db.py                   # PostgreSQL-Operationen
│   ├── db_config.py            # DB-Zugangsdaten
│   ├── openapc.py              # OpenAPC-Lader
│   ├── doaj.py                 # DOAJ-Lader
│   ├── pubmed.py               # PubMed-Parser
│   ├── enrichment.py           # logik für enricher
│   ├── constants.py            # constants zb eu ländern oder preis
│   ├── pubmed_enricher.py      # Anreicherung der Daten
│   └── insights.py             # Zusätzliche Analysen (z.B. unmatched ISSNs)
├── templates/                  # Template für html
│   └── index_string.html       # HTML layout 
├── utils/
│   ├── xml_to_csv_parser.py    # parst xml to csv
│   ├── download_pubmed_gz.py   # hunterlädt raw gz pubmed Daten
│   └── utils.py                # Hilfsfunktionen
├── data/                       # Daten (XML, CSV)
│   ├── pubmed_raw_to_csv/      # Daten, dass von pubmed huntergeladen und geparst sind
│   ├── pubmed_raw/             # Raw Daten, dass von pubmed huntergeladen in .gz format
│   └── journalcsv_doaj_.csv    # Doaj data,dass von doaj huntergeladen ist
├── requirements.txt      
└── README.md             


```
---

## 📦 Hinweis zur Bereitstellung der PubMed-Rohdaten

Aus Gründen der Speicherbegrenzung von GitHub wurden die ursprünglichen `.gz`-Dateien im Verzeichnis `data/pubmed_raw/` nicht mit in das Repository aufgenommen. Diese Dateien enthalten die vollständigen PubMed-XML-Datensätze im komprimierten Format und überschreiten die zulässige Upload-Größe.

Für eine vollständige lokale Reproduktion des Datenverarbeitungsprozesses können die entsprechenden Dateien jederzeit über das im Projekt enthaltene Skript heruntergeladen werden:

Das Skript befindet sich im Verzeichnis utils/ und heisst
download_pubmed_gz.py

Hinweis: Die Funktionalität des Dashboards ist auch ohne die .gz-Quelldateien gewährleistet, da bereits verarbeitete und extrahierte CSV-Dateien im Verzeichnis data/pubmed_raw_to_csv_test/ zur Verfügung stehen. Der erneute Download ist daher nur erforderlich, wenn eine vollständige Datenneuverarbeitung gewünscht ist.

## 📌 Hinweise

- Es werden nur Publikationen mit bekannten Kosten (`total_price_eur`) in den Diagrammen angezeigt.
- Nicht zuordenbare ISSNs erscheinen in der "Unmatched"-Tabelle.
- Manuelle Eingaben werden dauerhaft in der Datenbank gespeichert.
- CSV-Download enthält alle angereicherten Daten.
