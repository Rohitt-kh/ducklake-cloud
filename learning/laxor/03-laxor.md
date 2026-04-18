# Läxor — Modul 03: Deployment

## Förståelsefrågor

**1.** Varför behövs tre separata deployments (PostgreSQL, MinIO, API)?

**2.** Varför ska PostgreSQL och MinIO ha visibility "Private"?

**3.** Vad händer om du inte lägger till persistent storage på PostgreSQL?

**4.** Varför returnerar PostgreSQL "502 Bad Gateway" på KTH Cloud — är det ett fel?

**5.** Hur kommunicerar `ducklake-api` med `ducklake-postgres2` internt på KTH Cloud?

**6.** Vad är Kubernetes service discovery och varför orsakade det problem med POSTGRES_PORT?

**7.** Varför behöver MinIO en speciell health check-sökväg?

---

## Praktiska uppgifter

**8.** Logga in på KTH Cloud och titta på `ducklake-postgres2`. Hitta loggarna. Vad ser du?

**9.** Titta på miljövariablerna för `ducklake-api`. Förklara varför varje variabel finns.

**10.** I repot, öppna `docker-compose.yml`. Jämför miljövariablerna där med dem i KTH Cloud. Vad är lika och vad skiljer sig?

**11.** Vad händer om du startar om `ducklake-api` utan att `ducklake-postgres2` är igång?

---

## Diskussionsfrågor

**12.** Varför är det viktigt att starta deployments i rätt ordning (PostgreSQL → MinIO → API)?

**13.** Ge ett exempel på när Kubernetes service discovery kan orsaka problem och hur man löser det.

**14.** Om du skulle deploya samma system på Amazon AWS — vad skulle du använda istället för PostgreSQL-deployment och MinIO-deployment?
