# Läxor — Modul 02: DuckLake

## Förståelsefrågor

**1.** Vad är skillnaden mellan en datalake och en traditionell databas som PostgreSQL?

**2.** Vad är Parquet-formatet och varför är det bättre för analys än rad-baserade format?

**3.** DuckLake består av två delar — vad heter de och vad gör varje del?

**4.** Varför kan man inte ansluta direkt till DuckLake från en annan maskin utan ett API?

**5.** Vad menas med "time travel" i DuckLake-sammanhang?

**6.** Vad är DuckDB och hur skiljer det sig från PostgreSQL?

---

## Praktiska uppgifter

**7.** Öppna API-dokumentationen på:
```
https://ducklake-api.app.cloud.cbh.kth.se/docs
```
Räkna hur många endpoints som finns. Vilka kräver API-nyckel?

**8.** Hämta alla snapshots:
```bash
curl https://ducklake-api.app.cloud.cbh.kth.se/snapshots
```
Hur många snapshots finns det? Vad skapade dem?

**9.** Hämta alla datasets:
```bash
curl https://ducklake-api.app.cloud.cbh.kth.se/api/datasets
```
Vilka tabeller finns i laken? Vilka är "inbyggda" och vilka är "uppladdade"?

**10.** Titta på `api/database.py` i repot. Hitta raden där DuckLake "kopplas ihop" (ATTACH). Förklara vad den gör.

---

## Diskussionsfrågor

**11.** Netflix lagrar filmer i S3 och metadata i en databas. Hur liknar detta er DuckLake-setup?

**12.** När passar DuckLake och när passar PostgreSQL bättre?

**13.** Om du av misstag raderar all data från `lake.kunder` — hur kan du återställa den med time travel?
