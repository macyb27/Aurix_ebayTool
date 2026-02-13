# Agent-Review-Checkliste

## Zweck
Diese Checkliste dient dazu, Vorschläge anderer Agents (z.B. Feature-Agents, Backend-Agents) auf **Konsistenz**, **Sicherheit** und **Skalierbarkeit** mit der definierten Architektur zu prüfen.

---

## 1. Architektur-Konsistenz

### Service-Grenzen
- [ ] **Bounded Context**: Bleibt die Änderung innerhalb des zuständigen Services?
- [ ] **Datenbesitz**: Wird nur auf Daten des eigenen Services zugegriffen?
- [ ] **Kein DB-Cross-Access**: Kein direkter Zugriff auf Tabellen anderer Services
- [ ] **Abhängigkeiten**: Keine neuen zyklischen Abhängigkeiten eingeführt

### Kommunikation
- [ ] **Sync vs. Async**: Sind lange/blockierende Operationen als Events/Jobs modelliert?
- [ ] **Event-Format**: Verwendung von CloudEvents 1.0 bei neuen Events
- [ ] **API-Contract**: Entspricht die Schnittstelle den definierten Contracts (02-API-CONTRACTS.md)?

### Shared Kernel
- [ ] **IDs**: Verwendung von UUID für TenantId, UserId, ListingId, ProductId
- [ ] **Fehlercodes**: Einheitliches Fehlerformat (RFC 7807)
- [ ] **Pagination**: Standard-Pagination-Format bei Listen-Endpoints

---

## 2. Sicherheit

### Authentifizierung & Autorisierung
- [ ] **Auth**: Ist der Endpoint durch JWT/API-Key geschützt?
- [ ] **RBAC**: Werden Berechtigungen (z.B. `listings:write`) geprüft?
- [ ] **Service-to-Service**: Verwendung von mTLS oder Service-Token

### Tenant-Isolation
- [ ] **tenant_id**: In allen tenant-spezifischen Queries enthalten
- [ ] **Header**: X-Tenant-Id wird vom Gateway gesetzt und validiert
- [ ] **Kein Cross-Tenant**: Keine Möglichkeit, Daten eines anderen Tenants abzurufen

### Input & Secrets
- [ ] **Validierung**: Alle User-Inputs validiert (Länge, Format, Whitelist)
- [ ] **Sanitization**: Keine SQL-Injection, XSS-Risiken
- [ ] **Secrets**: Keine Hardcoded API-Keys, Passwörter, Tokens
- [ ] **Logs**: Keine sensiblen Daten in Logs (PII, Tokens)

### Externe Integration
- [ ] **eBay**: OAuth-Token verschlüsselt gespeichert
- [ ] **Webhooks**: Signatur-Validierung bei eingehenden Webhooks
- [ ] **AI-Provider**: API-Keys aus Vault/Env, nicht im Code

---

## 3. Skalierbarkeit

### Statelessness
- [ ] **Kein lokaler State**: Service-Instanzen sind austauschbar
- [ ] **Session**: Session-Daten in Redis, nicht in Memory
- [ ] **Sticky Sessions**: Nicht erforderlich

### Performance
- [ ] **DB-Indexe**: Neue Queries mit passenden Indexen
- [ ] **N+1**: Keine N+1-Query-Probleme
- [ ] **Timeout**: Externe API-Calls mit Timeout und Circuit Breaker
- [ ] **Caching**: Wo sinnvoll, Cache-Strategie definiert

### Async & Queues
- [ ] **Lange Operationen**: > 2s als async/Event
- [ ] **Retry**: Retry-Policy für fehlgeschlagene Events
- [ ] **Idempotenz**: Kritische Operationen idempotent (Idempotency-Key)

### Ressourcen
- [ ] **Connection Pool**: DB-Connections begrenzt
- [ ] **Memory**: Keine unbegrenzten In-Memory-Sammlungen
- [ ] **Rate-Limiting**: Bei externen APIs (eBay) eingehalten

---

## 4. SaaS-Fähigkeit

### Multi-Tenancy
- [ ] **Plan-Limits**: Usage-Check vor limitierten Operationen
- [ ] **Feature-Flags**: Feature nur bei entsprechendem Plan aktiv
- [ ] **Onboarding**: Self-Service-fähig (kein manueller Admin nötig)

### Billing & Usage
- [ ] **Usage-Tracking**: Bei limitierten Ressourcen (Listings, AI-Calls) aufgezeichnet
- [ ] **Tenant-Löschung**: Saubere Cascade, Export, Anonymisierung möglich

---

## 5. Dokumentation

- [ ] **API**: OpenAPI/Contract aktualisiert bei neuen Endpoints
- [ ] **Events**: Event-Schema in contracts/events dokumentiert
- [ ] **DB**: Migration-Skript bei Schema-Änderungen
- [ ] **Architektur**: Relevante Architektur-Docs aktualisiert

---

## 6. Bewertungsmatrix

| Kategorie | Gewichtung | Bestanden? |
|-----------|------------|------------|
| Architektur-Konsistenz | Hoch | ☐ |
| Sicherheit | Kritisch | ☐ |
| Skalierbarkeit | Hoch | ☐ |
| SaaS-Fähigkeit | Mittel | ☐ |
| Dokumentation | Mittel | ☐ |

**Empfehlung:**
- **Alle kritisch/hoch bestanden** → Vorschlag akzeptieren
- **Sicherheit nicht bestanden** → Vorschlag ablehnen
- **Einzelne Punkte offen** → Rückfrage an Agent mit konkreten Anforderungen

---

## 7. Referenz-Dokumente

- [00-ARCHITECTURE-OVERVIEW.md](./00-ARCHITECTURE-OVERVIEW.md)
- [01-SERVICE-BOUNDARIES.md](./01-SERVICE-BOUNDARIES.md)
- [02-API-CONTRACTS.md](./02-API-CONTRACTS.md)
- [03-DATABASE-SCHEMA.md](./03-DATABASE-SCHEMA.md)
- [04-EVENT-FLOWS.md](./04-EVENT-FLOWS.md)
- [05-SECURITY-SCALABILITY.md](./05-SECURITY-SCALABILITY.md)
