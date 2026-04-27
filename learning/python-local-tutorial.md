# Python Tutorial — Lokal DuckLake (utan moln)

## Hur Python ansluter till en lokal DuckLake

```
Python-skript → duckdb-bibliotek → DuckLake (catalog.db + lake-data/)
```

Ingen PostgreSQL, ingen MinIO, ingen Docker. Allt sparas som vanliga filer på din dator — du kör allt med bara `python` och `pip`.

---

## Vad är en lokal DuckLake?

En lokal DuckLake har samma två delar som molnversionen — men båda körs lokalt:

```
DuckLake (lokalt)
├── Katalog (catalog.db)
│   └── En DuckDB-fil — lagrar schema, snapshots, filreferenser
└── Data (lake-data/)
    └── En mapp med Parquet-filer — den faktiska datan
```

Du slipper all molnkonfiguration men får ändå DuckLakes fördelar: transaktioner, time travel och Parquet-lagring.

---

## Jämförelse: Lokalt vs Moln

| | Lokalt | Moln |
|--|--------|------|
| Katalog | `catalog.db` (fil) | PostgreSQL (server) |
| Lagring | `lake-data/` (mapp) | MinIO / S3 (bucket) |
| Kräver server | Nej | Ja |
| Passar för | Lärande, prototyper | Produktion |
| Delas med andra | Nej | Ja |
| Starttid | < 1 sekund | Minuter |

---

## Filstruktur

Projektet är uppdelat i **två delar** som delar samma lokala DuckLake:

```
python-local/
├── Del 1 — skript
│   └── setup.py            ← Skapar DuckLake och kör CRUD
│
├── Del 2 — API
│   ├── database.py         ← Anslutning till DuckLake
│   ├── main.py             ← FastAPI-endpoints
│   └── requirements.txt
│
├── catalog.db              ← Skapas automatiskt (katalog)
└── lake-data/              ← Skapas automatiskt (Parquet-filer)
```

`catalog.db` och `lake-data/` skapas första gången du kör `setup.py`. Del 2 läser från **exakt samma filer**.

---

## Del 1 — Python-skript (setup.py)

Skriptet skapar DuckLake, skapar en tabell och demonstrerar alla fyra CRUD-operationer.

### Steg 1 — Anslut till DuckLake

```python
import duckdb
import os

# Skapa data-mappen om den inte finns
os.makedirs("lake-data", exist_ok=True)

# Anslut och ladda DuckLake-extension
con = duckdb.connect()
con.execute("INSTALL ducklake; LOAD ducklake")

# Koppla katalog och datamapp — skapar catalog.db om den inte finns
con.execute("ATTACH 'ducklake:catalog.db' AS lake (DATA_PATH 'lake-data/')")
```

**Vad händer här?**

| Rad | Vad den gör |
|-----|-------------|
| `duckdb.connect()` | Skapar en in-memory DuckDB-instans |
| `INSTALL ducklake` | Laddar ner extension (bara första gången) |
| `LOAD ducklake` | Aktiverar extensionen |
| `ATTACH 'ducklake:catalog.db'` | Kopplar katalogen och datamappen |

`ATTACH` skapar `catalog.db` och `lake-data/` automatiskt om de inte finns.

### Steg 2 — Skapa tabell (CREATE TABLE)

```python
con.execute("""
    CREATE TABLE IF NOT EXISTS lake.students (
        id     INTEGER,
        name   VARCHAR NOT NULL,
        grade  DOUBLE
    )
""")
print("Tabell skapad: lake.students")
```

`IF NOT EXISTS` gör att det inte kraschar om du kör skriptet igen.

### Steg 3 — Lägg till rader (INSERT)

```python
con.execute("INSERT INTO lake.students VALUES (1, 'Alice',   9.5)")
con.execute("INSERT INTO lake.students VALUES (2, 'Bob',     8.0)")
con.execute("INSERT INTO lake.students VALUES (3, 'Charlie', 7.5)")
print("Lade till 3 studenter")
```

Varje `INSERT` skapar en ny snapshot i DuckLake — precis som en commit i git.

### Steg 4 — Läs data (SELECT)

```python
rows = con.execute("SELECT * FROM lake.students ORDER BY id").fetchall()

print("\n── Alla studenter ──")
for row in rows:
    print(f"  ID: {row[0]}, Namn: {row[1]}, Betyg: {row[2]}")
```

Förväntad utmatning:

```
── Alla studenter ──
  ID: 1, Namn: Alice, Betyg: 9.5
  ID: 2, Namn: Bob, Betyg: 8.0
  ID: 3, Namn: Charlie, Betyg: 7.5
```

### Steg 5 — Uppdatera rad (UPDATE)

```python
con.execute("UPDATE lake.students SET grade = 9.0 WHERE id = 2")
print("Uppdaterade Bobs betyg till 9.0")
```

### Steg 6 — Radera rad (DELETE)

```python
con.execute("DELETE FROM lake.students WHERE id = 3")
print("Raderade Charlie")
```

### Steg 7 — Time travel

Varje skrivoperation skapar automatiskt en ny **snapshot**. Du kan lista alla snapshots och läsa gammal data:

```python
# Visa alla snapshots
snapshots = con.execute(
    "SELECT snapshot_id, created FROM ducklake_snapshots('lake')"
).fetchall()

print("\n── Snapshots ──")
for s in snapshots:
    print(f"  Snapshot {s[0]}: {s[1]}")

# Läs data som den såg ut vid snapshot 1 (före uppdateringar)
gamla = con.execute(
    "SELECT * FROM lake.students AT (VERSION => 1)"
).fetchall()

print("\n── Data vid snapshot 1 ──")
for row in gamla:
    print(f"  {row}")
```

### Steg 8 — Stäng anslutningen

```python
con.close()
print("\nKlart! Kolla catalog.db och lake-data/ i din mapp.")
```

### Kör skriptet

```bash
pip install duckdb
python setup.py
```

Efteråt ska du ha:
- `catalog.db` — en ny fil (katalogen)
- `lake-data/` — en ny mapp med Parquet-filer

---

## Del 2 — FastAPI

API:et läser från **samma** `catalog.db` och `lake-data/` som skriptet skapade i Del 1.

### database.py — ansvar

Hanterar allt som har med DuckLake-anslutningen att göra:

```python
import duckdb
import os

os.makedirs("lake-data", exist_ok=True)


def get_conn() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    con.execute("INSTALL ducklake; LOAD ducklake")
    con.execute("ATTACH 'ducklake:catalog.db' AS lake (DATA_PATH 'lake-data/')")
    return con
```

Exakt samma tre rader som i `setup.py` — API:et och skriptet delar filen `catalog.db`.

**Viktigt:** Varje HTTP-anrop skapar en ny connection och stänger den efteråt — se `with get_conn() as con:` nedan.

### main.py — ansvar

Hanterar HTTP-anropen:

```python
from fastapi import FastAPI, HTTPException
from database import get_conn

app = FastAPI(title="DuckLake Local API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/datasets")
def lista_datasets():
    with get_conn() as con:
        tabeller = con.execute(
            "SELECT table_name FROM duckdb_tables() WHERE database_name = 'lake'"
        ).fetchall()
    return [{"name": r[0]} for r in tabeller]


@app.get("/datasets/students")
def get_students():
    with get_conn() as con:
        rows = con.execute(
            "SELECT id, name, grade FROM lake.students ORDER BY id"
        ).fetchall()
    return [{"id": r[0], "name": r[1], "grade": r[2]} for r in rows]
```

### Endpoints

| Endpoint | Metod | Vad den returnerar |
|----------|-------|--------------------|
| `/health` | GET | `{"status": "ok"}` |
| `/datasets` | GET | Lista med alla tabellnamn i DuckLake |
| `/datasets/students` | GET | Alla studenter som JSON |

### Kör API:et

```bash
pip install fastapi uvicorn duckdb
uvicorn main:app --reload
```

Testa sedan:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/datasets
curl http://localhost:8000/datasets/students
```

Eller öppna `http://localhost:8000/docs` för interaktiv API-dokumentation.

---

## FastAPI — viktiga begrepp

### Decorators

```python
@app.get("/health")             # Lyssnar på HTTP GET /health
@app.get("/datasets/students")  # Lyssnar på HTTP GET /datasets/students
```

En decorator är ett prefix som berättar för FastAPI vilken HTTP-metod och sökväg som gäller.

### Context manager — `with get_conn() as con:`

```python
with get_conn() as con:       # Öppnar anslutning
    rows = con.execute("SELECT ...").fetchall()
# Stängs automatiskt här — även om ett fel uppstår
```

`with`-blocket garanterar att DuckDB-anslutningen stängs korrekt. Det är säkrare än att anropa `con.close()` manuellt.

### Varför ny connection per anrop?

DuckDB är inte trådsäkert på connection-nivå — flera anrop kan inte dela samma connection-objekt. En connection per HTTP-anrop och `with`-block är det säkra mönstret.

---

## requirements.txt

```
fastapi==0.136.0    # Webbramverket
uvicorn==0.44.0     # ASGI-server som kör FastAPI
duckdb==1.5.2       # DuckDB + DuckLake-extension
```

Installera med:

```bash
pip install -r requirements.txt
```

---

## Viktiga fällor

1. **Kör `setup.py` innan API:et** — `catalog.db` och `lake-data/` måste finnas. Om du startar API:et utan att ha kört `setup.py` returnerar `/datasets/students` ett fel eftersom tabellen inte existerar.

2. **Kör båda från samma mapp** — `setup.py` och `uvicorn main:app` måste köras från **samma katalog**, annars hittar inte API:et `catalog.db`.

3. **`INSTALL ducklake` behövs bara första gången** — Men det är ofarligt att köra varje gång. DuckDB hoppar över installationen om extensionen redan finns.

4. **Dela inte connection mellan anrop** — Skapa en ny connection per anrop med `with get_conn() as con:`. Spara aldrig connection-objektet som en global variabel.

5. **Parquet-filer raderas inte automatiskt** — Varje snapshot lämnar kvar filer i `lake-data/`. Kör `CALL ducklake_cleanup('lake')` för att rensa bort oanvända filer.
