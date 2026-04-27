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
