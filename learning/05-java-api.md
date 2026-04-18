# Modul 05 — Java API

## Hur Java ansluter till DuckLake

```
HTTP-anrop → Spring Boot → DuckDB JDBC → DuckLake (PostgreSQL + MinIO)
```

Java ansluter **direkt** via JDBC-drivrutinen — ingen Python-mellanhand. Det är renare men kräver mer konfiguration.

---

## Jämförelse: Python vs Java

| | Python | Java |
|--|--------|------|
| Anslutning | duckdb-bibliotek | DuckDB JDBC-driver |
| Webbramverk | FastAPI | Spring Boot |
| Kräver Python? | Ja | **Nej** |
| Renhetsgrad | HTTP-mellanhand | Direkt JDBC |
| Komplexitet | Lägre | Högre |
| Versionsnummer (Maven) | Enkelt | Fyrsiffrigt (1.5.2.0) |

---

## Filstruktur

```
java-api/
├── pom.xml                          ← Maven-beroenden
├── Dockerfile
└── src/main/java/se/kth/ducklake/
    ├── DucklakeApp.java             ← Startpunkt
    ├── service/DuckLakeService.java ← Anslutning + SQL
    ├── controller/ApiController.java ← HTTP-endpoints
    └── model/                       ← Datamodeller (records)
```

---

## DuckLakeService.java — ansvar

Hanterar allt som har med DuckLake att göra:

### @PostConstruct — körs en gång vid start

```java
@PostConstruct
public void installExtensions() throws SQLException {
    // Installera extensions (laddas ner om de inte finns)
    try (Connection conn = DriverManager.getConnection("jdbc:duckdb:");
         Statement stmt = conn.createStatement()) {
        stmt.execute("INSTALL ducklake");
        stmt.execute("INSTALL postgres");
        stmt.execute("INSTALL httpfs");
    }
    seedIfEmpty(); // Fyll med exempeldata om tabellen är tom
}
```

### openConnection() — öppnas per anrop

```java
public Connection openConnection() throws SQLException {
    Connection conn = DriverManager.getConnection("jdbc:duckdb:");
    Statement stmt = conn.createStatement();

    stmt.execute("LOAD ducklake");
    stmt.execute("LOAD postgres");

    // Skapa secret (OBS: PORT måste vara hårdkodad — se fällor!)
    stmt.execute("""
        CREATE OR REPLACE SECRET (
            TYPE postgres,
            HOST '%s',
            PORT 5432,
            DATABASE '%s',
            USER '%s',
            PASSWORD '%s'
        )""".formatted(pgHost, pgDb, pgUser, pgPass));

    // Koppla DuckLake
    stmt.execute("ATTACH 'ducklake:postgres:dbname=" + pgDb
        + "' AS lake (DATA_PATH 's3://" + s3Bucket + "/')");

    return conn;
}
```

---

## ApiController.java — ansvar

Hanterar HTTP-anropen:

```java
@GetMapping("/api/kunder")
public List<Map<String, Object>> getKunder() throws Exception {
    return lake.query("SELECT id, namn, email FROM lake.kunder ORDER BY id");
}

@PostMapping("/api/kunder")
public ResponseEntity<?> nyKund(
        @RequestHeader(value = "X-API-Key", required = false) String key,
        @RequestBody NyKund kund) throws Exception {

    if (!validKey(key)) return unauthorized();  // Kolla API-nyckel

    int nid = ((Number) lake.scalar(
        "SELECT COALESCE(MAX(id),0)+1 FROM lake.kunder")).intValue();
    lake.update("INSERT INTO lake.kunder VALUES (?,?,?,?)",
        nid, kund.namn(), kund.email(), kund.telefon());

    return ResponseEntity.status(201).body(Map.of("id", nid));
}
```

---

## Spring Boot

Spring Boot är ett Java-ramverk för att bygga webbapplikationer.

### Viktiga annotationer

| Annotation | Vad den gör |
|------------|-------------|
| `@SpringBootApplication` | Markerar startpunkten |
| `@Service` | Markerar en service-klass |
| `@RestController` | Markerar en controller med REST-endpoints |
| `@GetMapping("/sökväg")` | HTTP GET-endpoint |
| `@PostMapping("/sökväg")` | HTTP POST-endpoint |
| `@DeleteMapping("/sökväg/{id}")` | HTTP DELETE-endpoint |
| `@Value("${property}")` | Injicerar ett värde från properties |
| `@PostConstruct` | Körs automatiskt efter att klassen skapats |

### Records (datamodeller)

```java
// Enkel datamodell — ersätter klasser med getters/setters
public record NyKund(String namn, String email, String telefon) {}
```

---

## application.properties

```properties
server.port=8080

# Använd eget prefix (ducklake.*) för att undvika Spring Boot-konflikter
ducklake.postgres.host=${POSTGRES_HOST:localhost}
ducklake.postgres.db=${POSTGRES_DB:ducklake}
ducklake.postgres.user=${POSTGRES_USER:duck}
ducklake.postgres.password=${POSTGRES_PASSWORD:postgres}
ducklake.s3.endpoint=${S3_ENDPOINT:}
ducklake.s3.bucket=${S3_BUCKET:ducklake}
ducklake.api.key=${API_KEY:change-me}
```

**Varför eget prefix?**
Spring Boot har inbyggda properties som kan krocka. `ducklake.postgres.host` är säkert, men `POSTGRES_PORT` kan skrivas över av Kubernetes.

---

## Viktiga fällor i Java (sammanfattning)

1. **POSTGRES_PORT** — Kubernetes skriver över det. Lösning: hårdkoda `PORT 5432`
2. **Versionnummer** — DuckDB JDBC heter `1.5.2.0` inte `1.5.2`
3. **eclipse-temurin** — använd `jammy` inte `slim` i Dockerfile
4. **Kolon i SQL** — undvik kolon i ATTACH-strängar, använd secret istället
5. **Cirkulär referens** — skriv `ducklake.s3.region=${S3_REGION:local}` inte `S3_REGION=${S3_REGION:local}`

---

➡️ [Gå till läxor för modul 05](laxor/05-laxor.md)
