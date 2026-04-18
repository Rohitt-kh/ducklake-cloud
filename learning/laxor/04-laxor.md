# Läxor — Modul 04: Python API

## Förståelsefrågor

**1.** Vad är skillnaden mellan `database.py` och `main.py` — vad ansvarar varje fil för?

**2.** Varför öppnas och stängs en ny DuckDB-anslutning för varje HTTP-anrop?

**3.** Vad är `@app.get`, `@app.post` och `@app.delete` för något?

**4.** Vad händer om du anropar en POST-endpoint utan `X-API-Key`-header?

**5.** Varför används `secrets.compare_digest` istället för vanlig `==` för att jämföra API-nycklar?

**6.** Vad gör `init_db()` och när körs den?

---

## Praktiska uppgifter

**7.** Lägg till en ny kund via API:et:
```bash
curl -X POST https://ducklake-api.app.cloud.cbh.kth.se/api/kunder \
  -H "Content-Type: application/json" \
  -H "X-API-Key: hemlig-nyckel" \
  -d '{"namn":"Ditt namn","email":"din@email.com"}'
```
Kontrollera att kunden lades till med GET.

**8.** Titta på `api/main.py` i repot. Hitta seed-logiken. Förklara varför den kontrollerar `COUNT(*) == 0`.

**9.** Lägg till en ny endpoint `/api/kunder/sok?q=anna` lokalt i koden (utan att deploya). Vad SQL-fråga skulle du köra?

**10.** Öppna `https://ducklake-api.app.cloud.cbh.kth.se/docs`. Testa ett anrop direkt från dokumentationen.

---

## Koduppgifter

**11.** Skriv en ny endpoint i Python som returnerar antal kunder:
```python
@app.get("/api/kunder/antal")
def antal_kunder():
    # Skriv din kod här
```

**12.** Skriv en endpoint som returnerar alla produkter med pris över 1000 kr.

---

## Diskussionsfrågor

**13.** Vad är nackdelen med att öppna en ny DuckDB-anslutning för varje anrop?

**14.** Varför är det viktigt att stänga anslutningen (`con.close()`) efter varje anrop?
