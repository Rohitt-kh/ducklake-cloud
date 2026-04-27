# Tutorial — DuckLake Locally with Python API

## Prerequisites

- Docker + Docker Compose
- Python 3.10+

---

## Part 1 — Set Up DuckLake Locally

### Step 1 — Start the services

Run the following command in this folder:

```bash
docker compose up -d
```

This starts three services:

| Service | Purpose | Port |
|---------|---------|------|
| PostgreSQL | DuckLake catalog (metadata) | 5432 |
| MinIO | Parquet storage (S3) | 9000 / 9001 |
| mc | Creates the bucket automatically | — |

The MinIO console is available at `http://localhost:9001` (user: `ducklake`, password: `minioadmin`).

---

### Step 2 — Open the DuckDB shell

**Linux/macOS:**

```bash
chmod +x shell.sh
./shell.sh
```

**Windows (PowerShell):**

```powershell
./shell.ps1
```

The DuckDB UI opens in your browser and `setup.sql` runs automatically — you are now connected to your DuckLake.

---

### Step 3 — Verify

Run in the DuckDB shell:

```sql
CREATE TABLE customers (id INTEGER, name VARCHAR, email VARCHAR);
INSERT INTO customers VALUES (1, 'Anna', 'anna@example.com');
SELECT * FROM customers;
```

If you see the row, DuckLake is working — metadata is stored in PostgreSQL and data as Parquet files in MinIO.

---

## Part 2 — Python API

Make sure Part 1 is running before continuing (`docker compose up -d`).

### Project structure

```
tutorial/
├── compose.yaml
├── setup.sql
├── shell.sh / shell.ps1
└── api/
    ├── requirements.txt
    ├── database.py
    └── main.py
```

---

### Step 1 — Install dependencies

```bash
cd api
pip install -r requirements.txt
```

---

### Step 2 — database.py

This file handles the connection to DuckLake. It connects DuckDB to PostgreSQL (catalog) and MinIO (Parquet storage) using the DuckLake extension.

```python
import duckdb
import os
from minio import Minio

POSTGRES_HOST     = os.getenv("POSTGRES_HOST",     "localhost")
POSTGRES_DB       = os.getenv("POSTGRES_DB",       "ducklake")
POSTGRES_USER     = os.getenv("POSTGRES_USER",     "duck")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "localhost:9000")
S3_KEY_ID   = os.getenv("S3_KEY_ID",   "ducklake")
S3_SECRET   = os.getenv("S3_SECRET",   "minioadmin")
S3_BUCKET   = os.getenv("S3_BUCKET",   "ducklake")


def ensure_bucket():
    client = Minio(S3_ENDPOINT, access_key=S3_KEY_ID, secret_key=S3_SECRET, secure=False)
    if not client.bucket_exists(S3_BUCKET):
        client.make_bucket(S3_BUCKET)


def get_conn() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()

    con.execute("INSTALL ducklake; LOAD ducklake")
    con.execute("INSTALL postgres;  LOAD postgres")

    con.execute(f"""
        CREATE OR REPLACE SECRET (
            TYPE     postgres,
            HOST     '{POSTGRES_HOST}',
            PORT     5432,
            DATABASE '{POSTGRES_DB}',
            USER     '{POSTGRES_USER}',
            PASSWORD '{POSTGRES_PASSWORD}'
        )
    """)

    con.execute("INSTALL httpfs; LOAD httpfs")
    con.execute(f"""
        CREATE OR REPLACE SECRET (
            TYPE      s3,
            KEY_ID    '{S3_KEY_ID}',
            SECRET    '{S3_SECRET}',
            REGION    'local',
            ENDPOINT  '{S3_ENDPOINT}',
            URL_STYLE 'path',
            USE_SSL   false
        )
    """)

    con.execute(f"""
        ATTACH 'ducklake:postgres:dbname={POSTGRES_DB}'
        AS my_lake (DATA_PATH 's3://{S3_BUCKET}/')
    """)

    return con


def init_db():
    with get_conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS my_lake.customers (
                id      INTEGER,
                name    VARCHAR NOT NULL,
                email   VARCHAR NOT NULL
            )
        """)
```

> A new DuckDB connection is created for each request. This is intentional — DuckLake uses snapshots and requires a fresh connection to see the latest data.

---

### Step 3 — main.py

A simple FastAPI application with three endpoints for the `customers` table.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from database import get_conn, init_db, ensure_bucket


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_bucket()
    init_db()
    yield


app = FastAPI(title="DuckLake API", lifespan=lifespan)


class NewCustomer(BaseModel):
    name: str
    email: str


@app.get("/customers")
def get_customers():
    with get_conn() as con:
        rows = con.execute(
            "SELECT id, name, email FROM my_lake.customers ORDER BY id"
        ).fetchall()
    return [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]


@app.post("/customers", status_code=201)
def create_customer(customer: NewCustomer):
    with get_conn() as con:
        new_id = con.execute(
            "SELECT COALESCE(MAX(id), 0) + 1 FROM my_lake.customers"
        ).fetchone()[0]
        con.execute(
            "INSERT INTO my_lake.customers VALUES (?, ?, ?)",
            [new_id, customer.name, customer.email]
        )
    return {"id": new_id, "name": customer.name, "email": customer.email}


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int):
    with get_conn() as con:
        con.execute("DELETE FROM my_lake.customers WHERE id = ?", [customer_id])
    return {"deleted": customer_id}


@app.get("/healthz")
def health():
    return {"status": "ok"}
```

---

### Step 4 — Run the API

```bash
uvicorn main:app --reload
```

The API is now available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

---

### Step 5 — Test the API

**Get all customers:**
```bash
curl http://localhost:8000/customers
```

**Create a customer:**
```bash
curl -X POST http://localhost:8000/customers \
  -H "Content-Type: application/json" \
  -d '{"name": "Anna", "email": "anna@example.com"}'
```

**Delete a customer:**
```bash
curl -X DELETE http://localhost:8000/customers/1
```
