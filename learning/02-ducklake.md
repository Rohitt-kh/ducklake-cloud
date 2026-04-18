# Modul 02 — DuckLake

## Vad är en datalake?

En **datalake** är ett centralt lager där data lagras i sitt råa format. Till skillnad från en traditionell databas lagras data som filer — inte i tabeller med lås och transaktioner.

```
Traditionell databas:    data → binärt format (proprietärt)
Datalake:                data → öppna filer (Parquet, CSV, JSON)
```

---

## Parquet-formatet

Parquet är ett **kolumnbaserat** filformat för strukturerad data.

### Rad-baserat vs Kolumnbaserat

```
Rad-baserat (PostgreSQL):
[id=1, namn="Anna", pris=100]
[id=2, namn="Erik", pris=200]

Kolumnbaserat (Parquet):
[id: 1, 2, 3, 4...]
[namn: "Anna", "Erik", "Maria"...]
[pris: 100, 200, 300...]
```

**Varför är kolumnbaserat bättre för analys?**

Om du vill beräkna genomsnittspris läser Parquet bara `pris`-kolumnen. PostgreSQL måste läsa hela raden för varje rad.

### Parquet i DuckLake

Du ser **aldrig** Parquet-filerna direkt — DuckLake hanterar dem automatiskt. Du skriver bara SQL:

```sql
INSERT INTO lake.produkter VALUES (1, 'Laptop', 9999.0)
-- DuckLake skapar/uppdaterar Parquet-filen bakom kulisserna
```

---

## DuckDB

DuckDB är en **inbäddad** analytisk databas — den körs inuti din applikation, ingen separat server behövs.

```python
import duckdb
con = duckdb.connect()  # Ingen server att starta!
con.execute("SELECT 1 + 1")
```

DuckDB kan läsa Parquet, CSV, JSON direkt:
```sql
SELECT * FROM read_parquet('data.parquet')
SELECT * FROM read_csv_auto('data.csv')
```

---

## DuckLake

DuckLake är ett **lakehouse-format** byggt ovanpå DuckDB. Det kombinerar fördelarna med en datalake (öppna filer) med fördelarna med en databas (transaktioner, schema).

### Två delar

```
DuckLake
├── Katalog (PostgreSQL)
│   └── Vilka tabeller finns? Hur ser de ut? Vilka snapshots?
└── Data (MinIO/S3)
    └── De faktiska Parquet-filerna med data
```

### Varför PostgreSQL som katalog?

- PostgreSQL är en stabil, vältestad databas för metadata
- Stöder transaktioner (ACID)
- Kan nås av flera applikationer samtidigt
- Alternativ: en enkel `.duckdb`-fil (bra för lokal utveckling men inte produktion)

### Varför MinIO som lagring?

- **S3-kompatibelt** — samma gränssnitt som Amazon S3
- Kan lagra obegränsade mängder filer
- Filerna är i öppet Parquet-format — kan läsas av Python, Spark, Pandas etc.

### Time Travel

Varje skrivoperation skapar en ny **snapshot**:

```sql
-- Se alla snapshots
SELECT * FROM ducklake_snapshots('lake')

-- Läs data som den såg ut vid snapshot 5
SELECT * FROM lake.kunder AT (VERSION => 5)
```

---

## Jämförelse: DuckLake vs PostgreSQL

| Egenskap | DuckLake | PostgreSQL |
|----------|----------|------------|
| Kräver server | Nej (filer) | Ja |
| Dataformat | Parquet (öppet) | Binärt (proprietärt) |
| Time travel | Ja | Nej |
| Analytiska queries | Snabb | Långsammare |
| Kan läsas av | Vad som helst | PostgreSQL-klient |
| Passar för | Analys, stora datamängder | Transaktionssystem |

---

## Varför behövs FastAPI/Spring Boot?

DuckLake är **inte** en server — det är bara filer och en katalog. Det kan inte ta emot nätverksanslutningar på egen hand.

```
UTAN API:
Java-app → ??? → DuckLake  (fungerar inte om de körs separat)

MED API:
Java-app → HTTP → FastAPI/Spring Boot → DuckLake  (fungerar!)
```

**Undantag:** Om Java-appen och DuckLake körs i **samma process** (som i Spring Boot + DuckDB JDBC) behövs inget separat API.

---

➡️ [Gå till läxor för modul 02](laxor/02-laxor.md)
