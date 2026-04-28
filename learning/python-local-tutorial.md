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

Du slipper all molnkonfiguration men får ändå DuckLakes fördelar: transaktioner och Parquet-lagring.

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
│   ├── student.py          ← Student-dataclass
│   ├── database.py         ← Anslutning till DuckLake
│   ├── main.py             ← FastAPI-endpoints
│   └── requirements.txt
│
├── catalog.db              ← Skapas automatiskt (katalog)
└── lake-data/              ← Skapas automatiskt (Parquet-filer)
```

`catalog.db` och `lake-data/` skapas första gången du kör `setup.py`. Del 2 läser från **exakt samma filer**.

---

# Del 1 — Python-skript (setup.py)


> **OBS – Windows-användare:** Om `python` eller `pip` inte fungerar, 
> prova `py` och `py -m pip` istället.
CRUD betyder:

```
C = Create (skapa)
R = Read   (läsa)
U = Update (uppdatera)
D = Delete (radera)
```

I SQL innebär det:

```
CREATE TABLE
INSERT INTO
SELECT
UPDATE
DELETE
```

---

## 1. Skapa projektfil och hello world

Skapa en fil `setup.py` med detta innehåll:

```python
print("DuckLake local lab started")
```

Kör skriptet:

```bash
python setup.py
```

Förväntad utmatning:

```
DuckLake local lab started
```

Om du ser den här utmatningen fungerar Python-miljön.

---

## 2. Installera duckdb

```bash
pip install duckdb
```

---

## 3. Anslut till DuckDB

Ersätt innehållet i `setup.py` med:

```python
import duckdb

con = duckdb.connect()
print("Connected to DuckDB")
con.close()
```

Kör skriptet:

```bash
python setup.py
```

Förväntad utmatning:

```
Connected to DuckDB
```

`duckdb.connect()` skapar en in-memory DuckDB-instans.

---

## 4. Skapa mappar och koppla DuckLake

Uppdatera `setup.py`:

```python
import duckdb
import os

os.makedirs("lake-data", exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL ducklake; LOAD ducklake")
con.execute("ATTACH 'ducklake:catalog.db' AS lake (DATA_PATH 'lake-data/')")
print("DuckLake is ready")
con.close()
```

Kör skriptet:

```bash
python setup.py
```

Förväntad utmatning:

```
DuckLake is ready
```

Det här är en av de viktigaste delarna i labben.

| Rad | Vad den gör |
|-----|-------------|
| `os.makedirs(...)` | Skapar `lake-data/`-mappen om den inte finns |
| `INSTALL ducklake` | Laddar ner extensionen (bara första gången) |
| `LOAD ducklake` | Aktiverar extensionen |
| `ATTACH 'ducklake:catalog.db'` | Kopplar katalogen och datamappen |

`ATTACH` skapar `catalog.db` och `lake-data/` automatiskt om de inte finns.

---

## 5. Skapa students-tabellen

Lägg till `CREATE TABLE` i `setup.py`, precis före `con.close()`:

```python
con.execute("""
    CREATE TABLE IF NOT EXISTS lake.students (
        id       INTEGER,
        name     VARCHAR NOT NULL,
        program  VARCHAR,
        credits  INTEGER
    )
""")
print("Tabell skapad: lake.students")
```

Kör skriptet:

```bash
python setup.py
```

Förväntad utmatning:

```
DuckLake is ready
Tabell skapad: lake.students
```

`IF NOT EXISTS` gör att det inte kraschar om du kör skriptet igen.

---

## 6. Lägg till Student-dataclass

Lägg till `Student`-dataklassen högst upp i `setup.py`, direkt efter importerna:

```python
from dataclasses import dataclass

@dataclass
class Student:
    id: int
    name: str
    program: str
    credits: int
```

En dataclass i Python motsvarar ett record i Java. Den grupperar fältvärdena för en student på ett strukturerat sätt.

Skriptet ska nu börja med:

```python
import duckdb
import os
from dataclasses import dataclass


@dataclass
class Student:
    id: int
    name: str
    program: str
    credits: int


os.makedirs("lake-data", exist_ok=True)
# ...
```

Kör skriptet:

```bash
python setup.py
```

Förväntad utmatning (samma som förut — dataclassen ändrar inget beteende ännu):

```
DuckLake is ready
Tabell skapad: lake.students
```

---

## 7. Lägg till rader (INSERT)

Lägg till INSERT-koden i `setup.py` efter `CREATE TABLE`, före `con.close()`:

```python
con.execute("DELETE FROM lake.students")

students = [
    Student(1, "Alice",   "Datateknik",    90),
    Student(2, "Bob",     "Medieteknik",   60),
    Student(3, "Charlie", "Elektroteknik", 45),
]

for s in students:
    con.execute(
        "INSERT INTO lake.students VALUES (?, ?, ?, ?)",
        [s.id, s.name, s.program, s.credits]
    )
print("Lade till 3 studenter")
```

Kör skriptet:

```bash
python setup.py
```

Förväntad utmatning:

```
DuckLake is ready
Tabell skapad: lake.students
Lade till 3 studenter
```

`DELETE FROM lake.students` tömmer tabellen innan vi lägger in data. Det gör att utmatningen alltid är densamma, oavsett hur många gånger du kör skriptet.

Varje `INSERT` skapar en ny snapshot i DuckLake — precis som en commit i git.

---

## 8. Läs data (SELECT)

Lägg till en hjälpfunktion `print_students` i `setup.py` — placera den direkt efter `Student`-dataclassen, före resten av koden:

```python
def print_students(con):
    rows = con.execute(
        "SELECT id, name, program, credits FROM lake.students ORDER BY id"
    ).fetchall()
    for row in rows:
        print(f"  id={row[0]}, name={row[1]}, program={row[2]}, credits={row[3]}")
```

Anropa sedan `print_students` efter INSERT-loopen:

```python
print("\n--- Efter INSERT ---")
print_students(con)
```

Kör skriptet:

```bash
python setup.py
```

Förväntad utmatning:

```
DuckLake is ready
Tabell skapad: lake.students
Lade till 3 studenter

--- Efter INSERT ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=60
  id=3, name=Charlie, program=Elektroteknik, credits=45
```

Du har nu genomfört `Read`-delen av CRUD.

---

## 9. Uppdatera rad (UPDATE)

Lägg till dessa rader i `setup.py` efter `print_students`-anropet:

```python
con.execute("UPDATE lake.students SET credits = 75 WHERE id = 2")

print("\n--- Efter UPDATE ---")
print_students(con)
```

Kör skriptet:

```bash
python setup.py
```

Förväntad utmatning efter uppdateringen:

```
--- Efter UPDATE ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=75
  id=3, name=Charlie, program=Elektroteknik, credits=45
```

Du har nu genomfört `Update`-delen av CRUD.

---

## 10. Radera rad (DELETE)

Lägg till dessa rader i `setup.py` efter UPDATE-steget:

```python
con.execute("DELETE FROM lake.students WHERE id = 3")

print("\n--- Efter DELETE ---")
print_students(con)
```

Kör skriptet:

```bash
python setup.py
```

Förväntad utmatning efter raderingen:

```
--- Efter DELETE ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=75
```

Du har nu genomfört `Delete`-delen av CRUD.

---

## 11. Kontrollera det slutliga setup.py

Det slutliga `setup.py` ska se ut så här:

```python
import duckdb
import os
from dataclasses import dataclass


@dataclass
class Student:
    id: int
    name: str
    program: str
    credits: int


def print_students(con):
    rows = con.execute(
        "SELECT id, name, program, credits FROM lake.students ORDER BY id"
    ).fetchall()
    for row in rows:
        print(f"  id={row[0]}, name={row[1]}, program={row[2]}, credits={row[3]}")


os.makedirs("lake-data", exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL ducklake; LOAD ducklake")
con.execute("ATTACH 'ducklake:catalog.db' AS lake (DATA_PATH 'lake-data/')")
print("DuckLake is ready")

con.execute("""
    CREATE TABLE IF NOT EXISTS lake.students (
        id       INTEGER,
        name     VARCHAR NOT NULL,
        program  VARCHAR,
        credits  INTEGER
    )
""")
print("Tabell skapad: lake.students")

con.execute("DELETE FROM lake.students")

students = [
    Student(1, "Alice",   "Datateknik",    90),
    Student(2, "Bob",     "Medieteknik",   60),
    Student(3, "Charlie", "Elektroteknik", 45),
]

for s in students:
    con.execute(
        "INSERT INTO lake.students VALUES (?, ?, ?, ?)",
        [s.id, s.name, s.program, s.credits]
    )
print("Lade till 3 studenter")

print("\n--- Efter INSERT ---")
print_students(con)

con.execute("UPDATE lake.students SET credits = 75 WHERE id = 2")

print("\n--- Efter UPDATE ---")
print_students(con)

con.execute("DELETE FROM lake.students WHERE id = 3")

print("\n--- Efter DELETE ---")
print_students(con)

con.close()
print("\nKlart! Kolla catalog.db och lake-data/ i din mapp.")
```

Kör skriptet en sista gång:

```bash
python setup.py
```

Förväntad utmatning:

```
DuckLake is ready
Tabell skapad: lake.students
Lade till 3 studenter

--- Efter INSERT ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=60
  id=3, name=Charlie, program=Elektroteknik, credits=45

--- Efter UPDATE ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=75
  id=3, name=Charlie, program=Elektroteknik, credits=45

--- Efter DELETE ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=75

Klart! Kolla catalog.db och lake-data/ i din mapp.
```

Om din utmatning matchar detta fungerar din lokala DuckLake CRUD-applikation.

Nu finns den lokala DuckLaken på disk. Del 2 kommer att återanvända exakt samma `catalog.db` och `lake-data/`.

---

# Del 2 — FastAPI

API:et läser från **samma** `catalog.db` och `lake-data/` som skriptet skapade i Del 1.

### student.py — Student-dataclass

Skapa filen `student.py` i samma mapp som `main.py`:

```python
from dataclasses import dataclass


@dataclass
class Student:
    id: int
    name: str
    program: str
    credits: int
```

Samma dataclass som i `setup.py` — nu i en egen fil som API:et kan importera.

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
from fastapi import FastAPI
from database import get_conn
from student import Student

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
            "SELECT id, name, program, credits FROM lake.students ORDER BY id"
        ).fetchall()
    return [Student(id=r[0], name=r[1], program=r[2], credits=r[3]) for r in rows]
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

Förväntad utmatning från `/datasets/students` (om du slutförde Del 1):

```json
[
  {"id": 1, "name": "Alice", "program": "Datateknik", "credits": 90},
  {"id": 2, "name": "Bob", "program": "Medieteknik", "credits": 75}
]
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
