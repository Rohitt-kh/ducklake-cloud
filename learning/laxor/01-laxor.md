# Läxor — Modul 01: Grundbegrepp

## Förståelsefrågor

Svara med egna ord utan att titta på modulen.

**1.** Vad är skillnaden mellan en Docker-image och en Docker-container?

**2.** Vad är syftet med en Dockerfile?

**3.** Vad händer när du pushar kod till GitHub och GitHub Actions triggas?

**4.** Förklara vad GET, POST och DELETE gör med egna ord.

**5.** Vad är GHCR och varför behöver KTH Cloud det?

**6.** Varför ska man aldrig skriva ett lösenord direkt i koden?

**7.** Vad är en miljövariabel och när används den?

---

## Praktiska uppgifter

**8.** Öppna en terminal och kör:
```bash
curl https://ducklake-api.app.cloud.cbh.kth.se/api/kunder
```
Vad får du tillbaka? Vilket HTTP-statuskod fick du?

**9.** Försök göra ett POST-anrop utan API-nyckel:
```bash
curl -X POST https://ducklake-api.app.cloud.cbh.kth.se/api/kunder \
  -H "Content-Type: application/json" \
  -d '{"namn":"Test","email":"test@test.com"}'
```
Vad händer? Vilket statuskod fick du och varför?

**10.** Titta på [github.com/WildRelation/ducklake-cloud](https://github.com/WildRelation/ducklake-cloud/blob/main/.github/workflows/docker.yml). Förklara vad varje steg i GitHub Actions-filen gör.

---

## Diskussionsfrågor (diskutera med gruppen)

**11.** Varför kör man databaser och API:er som separata containers istället för allt i en?

**12.** Om du skulle bygga en webbsida för ett bibliotek — vilka HTTP-endpoints skulle du behöva?

**13.** Vad är nackdelen med att hårdkoda en port (t.ex. 5432) i koden?
