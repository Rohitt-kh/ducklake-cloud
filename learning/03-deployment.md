# Modul 03 — Deployment på KTH Cloud

## Vad är KTH Cloud?

KTH Cloud är en **Kubernetes-baserad** molnplattform. Du deployar Docker-images och plattformen hanterar körning, nätverksåtkomst och lagring.

---

## Kubernetes — grunderna

Kubernetes är ett system för att köra och hantera containers i produktion.

### Viktiga begrepp

| Begrepp | Förklaring |
|---------|------------|
| **Pod** | En körande container |
| **Service** | Nätverksadress för en pod |
| **Deployment** | Konfiguration för hur en pod ska köras |
| **Namespace** | Isolerad miljö (t.ex. "Flemingsberg") |

### Service Discovery

Kubernetes skapar automatiskt **miljövariabler** för alla services i ett namespace:

```
Service heter "postgres" → Kubernetes injicerar:
POSTGRES_PORT=tcp://10.43.x.x:5432
POSTGRES_HOST=10.43.x.x
```

**Detta är en viktig fallgrop** — om du sätter en miljövariabel med samma namn kan Kubernetes skriva över den!

---

## Deployment på KTH Cloud

### Tre deployments och varför

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   PostgreSQL    │   │     MinIO       │   │    FastAPI/     │
│   (Private)     │   │   (Private)     │   │  Spring Boot    │
│                 │   │                 │   │   (Public)      │
│  Port: 5432     │   │  Port: 9000     │   │  Port: 8000/80  │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

- **PostgreSQL och MinIO** är private — de ska inte vara nåbara utifrån
- **API:et** är public — det är det enda klienter pratar med

### Persistent Storage

**Problem:** Containers är tillfälliga. Varje gång en container startas om börjar den från noll.

**Lösning:** Koppla en persistent volym till en sökväg i containern:

```
Container /var/lib/postgresql/data → KTH Cloud disk (persistent)
```

Om du glömmer persistent storage försvinner all data vid omstart!

### Intern kommunikation

På KTH Cloud kan deployments nå varandra via **deployment-namnet** som hostname:

```python
POSTGRES_HOST = "ducklake-postgres2"  # Deployment-namn = DNS-namn
```

Du behöver inte veta IP-adressen — Kubernetes löser upp det automatiskt.

### Visibility

| Inställning | Vad det betyder | När man använder det |
|-------------|-----------------|---------------------|
| Public | Nåbar från internet | API, webbsidor |
| Private | Bara nåbar internt | Databaser, lagring |
| Private (Auth Proxy) | Nåbar med inloggning | Admin-gränssnitt |

---

## Miljövariabler på KTH Cloud

### Vad varje variabel gör

```
POSTGRES_HOST     → Adressen till PostgreSQL (deployment-namn)
POSTGRES_DB       → Vilket databasnamn som ska användas
POSTGRES_USER     → Användarnamnet
POSTGRES_PASSWORD → Lösenordet
S3_ENDPOINT       → Adressen till MinIO (deployment-namn:port)
S3_KEY_ID         → MinIO-användarnamn
S3_SECRET         → MinIO-lösenord
S3_BUCKET         → Namn på "mappen" i MinIO
API_KEY           → Skyddar POST/DELETE-endpoints
PORT              → Porten din app lyssnar på
```

### Varför inte hårdkoda värden i koden?

```python
# DÅLIGT — synligt för alla på GitHub!
POSTGRES_PASSWORD = "hemlig123"

# BRA — sätts i KTH Cloud, aldrig i koden
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "default")
```

### Kubernetes-konflikten med POSTGRES_PORT

Kubernetes injicerar automatiskt `POSTGRES_PORT=tcp://IP:PORT` för services. Detta skriver över ditt värde `5432`.

**Lösning:** Hårdkoda port 5432 i koden eller använd ett annat variabelnamn som inte krockar.

---

## Health Check

KTH Cloud kontrollerar regelbundet att din app är igång via en HTTP-förfrågan till en sökväg.

| App | Health check-sökväg |
|-----|---------------------|
| FastAPI/Spring Boot | `/healthz` |
| MinIO | `/minio/health/live` |
| PostgreSQL | (PostgreSQL pratar inte HTTP — 502 är normalt) |

---

➡️ [Gå till läxor för modul 03](laxor/03-laxor.md)
