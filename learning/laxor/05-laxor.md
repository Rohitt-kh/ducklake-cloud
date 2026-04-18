# Läxor — Modul 05: Java API

## Förståelsefrågor

**1.** Vad är den stora arkitekturskillnaden mellan Python-API:et och Java-API:et?

**2.** Vad gör `@PostConstruct` och varför är det viktigt för DuckLake?

**3.** Varför måste DuckDB JDBC-versionen vara `1.5.2.0` och inte `1.5.2`?

**4.** Vad är ett Java Record och varför används det för datamodeller?

**5.** Varför kan man inte använda `POSTGRES_PORT` som miljövariabel i Java-appen på KTH Cloud?

**6.** Vad är `@Value("${ducklake.postgres.host}")` och var läser den värdet ifrån?

**7.** Vad är skillnaden mellan `@Service` och `@RestController`?

---

## Praktiska uppgifter

**8.** Testa Java-API:et:
```bash
curl https://duckalakejava-api.app.cloud.cbh.kth.se/api/kunder
curl https://duckalakejava-api.app.cloud.cbh.kth.se/api/produkter
curl https://duckalakejava-api.app.cloud.cbh.kth.se/api/datasets
```
Jämför svaren med Python-API:et. Är de likadana?

**9.** Titta på `java-api/src/main/java/se/kth/ducklake/service/DuckLakeService.java`. Hitta `seedIfEmpty()`. Förklara logiken.

**10.** Titta på `application.properties`. Varför har alla properties prefixet `ducklake.`?

**11.** Lägg till en ny kund via Java-API:et:
```bash
curl -X POST https://duckalakejava-api.app.cloud.cbh.kth.se/api/kunder \
  -H "Content-Type: application/json" \
  -H "X-API-Key: hemlig-nyckel" \
  -d '{"namn":"Java Test","email":"java@test.com"}'
```
Verifiera sedan att kunden också syns i Python-API:et. Varför syns den där?

---

## Koduppgifter

**12.** Skriv en ny endpoint i Java som returnerar antal kunder:
```java
@GetMapping("/api/kunder/antal")
public Map<String, Object> antalKunder() throws Exception {
    // Skriv din kod här
}
```

**13.** Lägg till en `NyVader`-record och en GET-endpoint för en väder-tabell i Java.

---

## Diskussionsfrågor

**14.** Python-API:et använder en HTTP-mellanhand medan Java ansluter direkt. Vilka för- och nackdelar har varje approach?

**15.** Om du skapade en kund via Java-API:et — varför syns den också i Python-API:et?

**16.** Varför tar Java-appen ~60-80 sekunder att starta medan Python-appen startar på ~5 sekunder?
