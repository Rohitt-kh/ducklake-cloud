# DuckLake Cloud

En DuckLake-datalake med **PostgreSQL** som katalog och **MinIO** som Parquet-lagring — det produktionsliknande upplägget som DuckLake är designat för.

## Arkitektur

```
Klient (Python/Java)  →HTTP→  FastAPI  →duckdb→  DuckLake
                                                 ↙        ↘
                                          PostgreSQL     MinIO
                                          (katalog)    (Parquet)
```

## Starta lokalt

```bash
docker compose up --build
```

API tillgängligt på `http://localhost:8000`
MinIO-konsol på `http://localhost:9001` (minioadmin/minioadmin)

## Driftsätt på KTH Cloud

Tre deployments behövs:

### 1. PostgreSQL
- Image: `postgres:16-alpine`
- Port: `5432`
- Miljövariabler: `POSTGRES_DB=ducklake`, `POSTGRES_USER=duck`, `POSTGRES_PASSWORD=<lösenord>`

### 2. MinIO
- Image: `minio/minio`
- Port: `9000`
- Miljövariabler: `MINIO_ROOT_USER=minioadmin`, `MINIO_ROOT_PASSWORD=<lösenord>`
- Image start arguments: `server /data`

### 3. API
- Image: `ghcr.io/wildrelation/ducklake-cloud:latest`
- Port: `8000`
- Miljövariabler:
  - `POSTGRES_HOST` = `<postgres-deployment-url>`
  - `POSTGRES_DB` = `ducklake`
  - `POSTGRES_USER` = `duck`
  - `POSTGRES_PASSWORD` = `<lösenord>`
  - `S3_ENDPOINT` = `<minio-deployment-url>:9000`
  - `S3_KEY_ID` = `minioadmin`
  - `S3_SECRET` = `<lösenord>`
  - `S3_BUCKET` = `ducklake`
  - `API_KEY` = `<ditt-hemliga-lösenord>`

## Endpoints

| Metod | Endpoint | Auth |
|-------|----------|------|
| GET | `/api/kunder` | Nej |
| GET | `/api/produkter` | Nej |
| GET | `/api/ordrar` | Nej |
| POST | `/api/kunder` | **Ja** |
| POST | `/api/produkter` | **Ja** |
| POST | `/api/ordrar` | **Ja** |
| DELETE | `/api/kunder/{id}` | **Ja** |
| DELETE | `/api/produkter/{id}` | **Ja** |
| GET | `/api/datasets` | Nej |
| GET | `/api/datasets/{namn}` | Nej |
| POST | `/api/datasets/upload` | **Ja** |

Skrivoperationer kräver headern `X-API-Key: <lösenord>`.
