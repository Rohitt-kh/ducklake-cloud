# Python Tutorial — Local DuckLake (without cloud)

## How Python connects to a local DuckLake

```
Python script → duckdb library → DuckLake (catalog.db + lake-data/)
```

No PostgreSQL, no MinIO, no Docker. Everything is saved as regular files on your computer — you run everything with just `python` and `pip`.

---

## What is a local DuckLake?

A local DuckLake has the same two parts as the cloud version — but both run locally:

```
DuckLake (local)
├── Catalog (catalog.db)
│   └── A DuckDB file — stores schema, snapshots, file references
└── Data (lake-data/)
    └── A folder with Parquet files — the actual data
```

You skip all the cloud configuration but still get DuckLake's benefits: transactions and Parquet storage.

---

## Comparison: Local vs Cloud

| | Local | Cloud |
|--|-------|-------|
| Catalog | `catalog.db` (file) | PostgreSQL (server) |
| Storage | `lake-data/` (folder) | MinIO / S3 (bucket) |
| Requires server | No | Yes |
| Good for | Learning, prototypes | Production |
| Shared with others | No | Yes |
| Startup time | < 1 second | Minutes |

---

## 1. What you will build

The project is split into **two parts** that share the same local DuckLake:

```
python-local/
├── Part 1 — script
│   └── setup.py            ← Creates DuckLake and runs CRUD
│
├── Part 2 — API
│   ├── student.py          ← Student dataclass
│   ├── database.py         ← Connection to DuckLake
│   ├── main.py             ← FastAPI endpoints
│   └── requirements.txt
│
├── catalog.db              ← Created automatically (catalog)
└── lake-data/              ← Created automatically (Parquet files)
```

`catalog.db` and `lake-data/` are created the first time you run `setup.py`. Part 2 reads from **exactly the same files**.

---

## 2. Requirements

Before starting, make sure you have:

- Python 3.10+
- pip
- An internet connection the first time DuckDB installs the DuckLake extension

The `requirements.txt` file contains:

```
fastapi==0.136.0
uvicorn==0.44.0
duckdb==1.5.2
```

---

# Part 1 — Python script (setup.py)

CRUD means:

```
C = Create
R = Read
U = Update
D = Delete
```

In SQL, this means:

```
CREATE TABLE
INSERT INTO
SELECT
UPDATE
DELETE
```

---

## 1. Create a project file and hello world

Create a file `setup.py` with this content:

```python
print("DuckLake local lab started")
```

Run the script:

```bash
python setup.py
```

Expected output:

```
DuckLake local lab started
```

If you see this output, your Python environment is working.

---

## 2. Install duckdb

```bash
pip install duckdb
```

> **Note for Windows users:** If `pip` is not recognized, run this instead:
> ```bash
> py -m pip install duckdb
> ```

## 3. Connect to DuckDB

Replace the content of `setup.py` with:

```python
import duckdb

con = duckdb.connect()
print("Connected to DuckDB")
con.close()
```

Run the script:

```bash
python setup.py
```

Expected output:

```
Connected to DuckDB
```

`duckdb.connect()` creates an in-memory DuckDB instance.

---

## 4. Create folders and attach DuckLake

Update `setup.py`:

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

Run the script:

```bash
python setup.py
```

Expected output:

```
DuckLake is ready
```

This is one of the most important parts of the lab.

| Line | What it does |
|------|-------------|
| `os.makedirs(...)` | Creates the `lake-data/` folder if it does not exist |
| `INSTALL ducklake` | Downloads the extension (first time only) |
| `LOAD ducklake` | Activates the extension |
| `ATTACH 'ducklake:catalog.db'` | Attaches the catalog and data folder |

`ATTACH` creates `catalog.db` and `lake-data/` automatically if they do not exist.

---

## 5. Create the students table

Add `CREATE TABLE` to `setup.py`, just before `con.close()`:

```python
con.execute("""
    CREATE TABLE IF NOT EXISTS lake.students (
        id       INTEGER,
        name     VARCHAR NOT NULL,
        program  VARCHAR,
        credits  INTEGER
    )
""")
print("Table created: lake.students")
```

Run the script:

```bash
python setup.py
```

Expected output:

```
DuckLake is ready
Table created: lake.students
```

`IF NOT EXISTS` prevents a crash if you run the script again.

---

## 6. Add the Student dataclass

Add the `Student` dataclass at the top of `setup.py`, directly after the imports:

```python
from dataclasses import dataclass

@dataclass
class Student:
    id: int
    name: str
    program: str
    credits: int
```

A dataclass in Python is equivalent to a record in Java. It groups the field values for a student in a structured way.

The script should now begin with:

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

Run the script:

```bash
python setup.py
```

Expected output (same as before — the dataclass does not change the behavior yet):

```
DuckLake is ready
Table created: lake.students
```

---

## 7. Insert rows (INSERT)

Add the INSERT code to `setup.py` after `CREATE TABLE`, before `con.close()`:

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
print("Added 3 students")
```

Run the script:

```bash
python setup.py
```

Expected output:

```
DuckLake is ready
Table created: lake.students
Added 3 students
```

`DELETE FROM lake.students` clears the table before inserting data. This makes the output the same every time you run the script.

Each `INSERT` creates a new snapshot in DuckLake — just like a commit in git.

---

## 8. Read data (SELECT)

Add a helper function `print_students` to `setup.py` — place it directly after the `Student` dataclass, before the rest of the code:

```python
def print_students(con):
    rows = con.execute(
        "SELECT id, name, program, credits FROM lake.students ORDER BY id"
    ).fetchall()
    for row in rows:
        print(f"  id={row[0]}, name={row[1]}, program={row[2]}, credits={row[3]}")
```

Then call `print_students` after the INSERT loop:

```python
print("\n--- After INSERT ---")
print_students(con)
```

Run the script:

```bash
python setup.py
```

Expected output:

```
DuckLake is ready
Table created: lake.students
Added 3 students

--- After INSERT ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=60
  id=3, name=Charlie, program=Elektroteknik, credits=45
```

You have now completed the `Read` part of CRUD.

---

## 9. Update a row (UPDATE)

Add these lines to `setup.py` after the `print_students` call:

```python
con.execute("UPDATE lake.students SET credits = 75 WHERE id = 2")

print("\n--- After UPDATE ---")
print_students(con)
```

Run the script:

```bash
python setup.py
```

Expected output after the update:

```
--- After UPDATE ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=75
  id=3, name=Charlie, program=Elektroteknik, credits=45
```

You have now completed the `Update` part of CRUD.

---

## 10. Delete a row (DELETE)

Add these lines to `setup.py` after the UPDATE step:

```python
con.execute("DELETE FROM lake.students WHERE id = 3")

print("\n--- After DELETE ---")
print_students(con)
```

Run the script:

```bash
python setup.py
```

Expected output after the delete:

```
--- After DELETE ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=75
```

You have now completed the `Delete` part of CRUD.

---

## 11. Check your final setup.py

The final `setup.py` should look like this:

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
print("Table created: lake.students")

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
print("Added 3 students")

print("\n--- After INSERT ---")
print_students(con)

con.execute("UPDATE lake.students SET credits = 75 WHERE id = 2")

print("\n--- After UPDATE ---")
print_students(con)

con.execute("DELETE FROM lake.students WHERE id = 3")

print("\n--- After DELETE ---")
print_students(con)

con.close()
print("\nDone! Check catalog.db and lake-data/ in your folder.")
```

Run the script one final time:

```bash
python setup.py
```

Expected output:

```
DuckLake is ready
Table created: lake.students
Added 3 students

--- After INSERT ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=60
  id=3, name=Charlie, program=Elektroteknik, credits=45

--- After UPDATE ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=75
  id=3, name=Charlie, program=Elektroteknik, credits=45

--- After DELETE ---
  id=1, name=Alice, program=Datateknik, credits=90
  id=2, name=Bob, program=Medieteknik, credits=75

Done! Check catalog.db and lake-data/ in your folder.
```

If your output matches this, your local DuckLake CRUD application works.

The local DuckLake now exists on disk. Part 2 will reuse exactly the same `catalog.db` and `lake-data/`.

---

# Part 2 — FastAPI

The API reads from the **same** `catalog.db` and `lake-data/` that the script created in Part 1.

### student.py — Student dataclass

Create the file `student.py` in the same folder as `main.py`:

```python
from dataclasses import dataclass


@dataclass
class Student:
    id: int
    name: str
    program: str
    credits: int
```

The same dataclass as in `setup.py` — now in its own file that the API can import.

### database.py — responsibilities

Handles everything related to the DuckLake connection:

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

Exactly the same three lines as in `setup.py` — the API and the script share the `catalog.db` file.

**Important:** Each HTTP request creates a new connection and closes it afterwards — see `with get_conn() as con:` below.

### main.py — responsibilities

Handles the HTTP requests:

```python
from fastapi import FastAPI
from database import get_conn
from student import Student

app = FastAPI(title="DuckLake Local API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/datasets")
def list_datasets():
    with get_conn() as con:
        tables = con.execute(
            "SELECT table_name FROM duckdb_tables() WHERE database_name = 'lake'"
        ).fetchall()
    return [{"name": r[0]} for r in tables]


@app.get("/datasets/students")
def get_students():
    with get_conn() as con:
        rows = con.execute(
            "SELECT id, name, program, credits FROM lake.students ORDER BY id"
        ).fetchall()
    return [Student(id=r[0], name=r[1], program=r[2], credits=r[3]) for r in rows]
```

### Endpoints

| Endpoint | Method | What it returns |
|----------|--------|----------------|
| `/health` | GET | `{"status": "ok"}` |
| `/datasets` | GET | List of all table names in DuckLake |
| `/datasets/students` | GET | All students as JSON |

### Run the API

Install the packages:

```bash
pip install fastapi uvicorn duckdb
```

Start the API:

```bash
uvicorn main:app --reload
```

Then test:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/datasets
curl http://localhost:8000/datasets/students
```

Expected output from `/datasets/students` (if you completed Part 1):

```json
[
  {"id": 1, "name": "Alice", "program": "Datateknik", "credits": 90},
  {"id": 2, "name": "Bob", "program": "Medieteknik", "credits": 75}
]
```

Or open `http://localhost:8000/docs` for interactive API documentation.

---

## FastAPI — key concepts

### Decorators

```python
@app.get("/health")             # Listens to HTTP GET /health
@app.get("/datasets/students")  # Listens to HTTP GET /datasets/students
```

A decorator is a prefix that tells FastAPI which HTTP method and path to use.

### Context manager — `with get_conn() as con:`

```python
with get_conn() as con:       # Opens connection
    rows = con.execute("SELECT ...").fetchall()
# Closed automatically here — even if an error occurs
```

The `with` block guarantees that the DuckDB connection is closed correctly. It is safer than calling `con.close()` manually.

### Why a new connection per request?

DuckDB is not thread-safe at the connection level — multiple requests cannot share the same connection object. One connection per HTTP request with a `with` block is the safe pattern.

---

## requirements.txt

```
fastapi==0.136.0
uvicorn==0.44.0
duckdb==1.5.2
```

Install with:

```bash
pip install -r requirements.txt
```

---

## Common pitfalls

1. **Run `setup.py` before the API** — `catalog.db` and `lake-data/` must exist. If you start the API without having run `setup.py`, `/datasets/students` will return an error because the table does not exist.

2. **Run both from the same folder** — `setup.py` and `uvicorn main:app` must be run from the **same directory**, otherwise the API will not find `catalog.db`.

3. **`INSTALL ducklake` is only needed the first time** — But it is harmless to run every time. DuckDB skips the installation if the extension is already installed.

4. **Do not share connections between requests** — Create a new connection per request with `with get_conn() as con:`. Never save the connection object as a global variable.

5. **Parquet files are not deleted automatically** — Each snapshot leaves files in `lake-data/`. Run `CALL ducklake_cleanup('lake')` to remove unused files.
