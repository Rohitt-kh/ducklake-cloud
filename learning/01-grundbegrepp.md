# Modul 01 — Grundbegrepp

## Docker

### Vad är Docker?

Docker är ett verktyg för att paketera ett program och allt det behöver (bibliotek, inställningar, operativsystem) i en **container**. En container fungerar likadant oavsett var den körs — på din laptop, på en server, eller i molnet.

### Image vs Container

| Begrepp | Förklaring | Analogi |
|---------|------------|---------|
| **Image** | En mall/recept | Kakformen |
| **Container** | En körande instans av imagen | Kakan du bakat |

Du bygger en image en gång och kan starta hur många containers som helst från den.

### Dockerfile

En Dockerfile är instruktionerna för att bygga en image:

```dockerfile
FROM python:3.12-slim      # Utgå från denna bas-image
WORKDIR /app               # Arbeta i denna mapp
COPY requirements.txt .    # Kopiera filer
RUN pip install -r requirements.txt  # Kör kommandon
COPY . .                   # Kopiera resten
CMD ["uvicorn", "main:app"] # Vad som körs när containern startar
```

### Varför Docker?

- **Portabilitet** — fungerar likadant överallt
- **Isolering** — varje container är oberoende
- **Reproducerbarhet** — exakt samma miljö varje gång

---

## GitHub Actions och GHCR

### Vad är GitHub Actions?

Ett CI/CD-verktyg inbyggt i GitHub. Det kör automatiskt när du pushar kod — t.ex. bygger och pushar en Docker-image.

```
Du pushar kod → GitHub Actions triggas → Bygger Docker-image → Pushar till GHCR
```

### Vad är GHCR?

**GitHub Container Registry** — ett ställe att lagra Docker-images, kopplat till ditt GitHub-konto.

Din image-adress: `ghcr.io/<användarnamn>/<repo>:latest`

### Varför behövs det?

KTH Cloud hämtar din image från GHCR när du deployar. Utan det kan KTH Cloud inte hitta din kod.

---

## REST API

### Vad är ett API?

**API** (Application Programming Interface) är ett gränssnitt som låter program prata med varandra. Ett **REST API** kommunicerar via HTTP — samma protokoll som webbläsare använder.

### HTTP-metoder

| Metod | Vad den gör | Exempel |
|-------|-------------|---------|
| **GET** | Hämtar data | Hämta alla kunder |
| **POST** | Skapar ny data | Lägg till en kund |
| **DELETE** | Raderar data | Ta bort en kund |
| **PUT/PATCH** | Uppdaterar data | Ändra kundens namn |

### Request och Response

```
Klient                          Server
  │                               │
  │── GET /api/kunder ───────────>│
  │                               │ (kör SQL, hämtar data)
  │<── 200 OK + JSON-data ────────│
```

### HTTP-statuskoder

| Kod | Betydelse |
|-----|-----------|
| 200 | OK — lyckades |
| 201 | Created — skapad |
| 401 | Unauthorized — fel lösenord |
| 404 | Not Found — finns inte |
| 500 | Internal Server Error — något gick fel på servern |

### Varför JSON?

JSON är ett textformat som alla programmeringsspråk kan läsa. Det är standarden för att skicka data mellan program via HTTP.

```json
[
  {"id": 1, "namn": "Anna Svensson", "email": "anna@example.com"},
  {"id": 2, "namn": "Erik Johansson", "email": "erik@example.com"}
]
```

---

## Miljövariabler

### Vad är miljövariabler?

Variabler som sätts utanför koden — i operativsystemet eller i deployment-plattformen. Det gör att samma kod kan fungera i olika miljöer utan att ändra koden.

```python
# DÅLIGT — lösenord i koden (visas på GitHub!)
PASSWORD = "hemlig123"

# BRA — läser från miljö
PASSWORD = os.getenv("DB_PASSWORD", "default")
```

### Varför är det viktigt?

- Hemligheter (lösenord, API-nycklar) ska aldrig vara i koden
- Samma kod kan köras lokalt och i produktion med olika värden
- Enkelt att ändra utan att bygga om hela applikationen

---

➡️ [Gå till läxor för modul 01](laxor/01-laxor.md)
