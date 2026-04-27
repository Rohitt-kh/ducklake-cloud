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

*Coming soon.*
