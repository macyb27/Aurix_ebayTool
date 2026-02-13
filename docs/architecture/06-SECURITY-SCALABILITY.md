# Sicherheit und Skalierbarkeit

## 1. Sicherheitsarchitektur

### 1.1 Zero-Trust-Prinzipien

| Prinzip | Umsetzung |
|---------|-----------|
| **Never trust, always verify** | Jeder Request wird authentifiziert und autorisiert |
| **Least privilege** | RBAC mit minimalen Berechtigungen pro Rolle |
| **Assume breach** | Verschlüsselung, Audit-Logs, Segmentierung |
| **Micro-segmentation** | Services nur über definierte Ports erreichbar |

### 1.2 Authentifizierung

| Aspekt | Spezifikation |
|--------|---------------|
| **Mechanismus** | JWT (RS256) oder Opaque Tokens |
| **Access Token** | Kurzlebig (15–60 Min) |
| **Refresh Token** | Langlebig (7–30 Tage), rotierbar |
| **Storage** | HttpOnly, Secure, SameSite Cookies ODER Memory (SPA) |
| **OAuth2** | Für eBay, optional Google/Microsoft Login |

**JWT Claims (Access Token):**
```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "email": "user@example.com",
  "roles": ["member"],
  "iat": 1234567890,
  "exp": 1234571490
}
```

### 1.3 Autorisierung (RBAC)

| Rolle | Berechtigungen |
|-------|----------------|
| **owner** | Tenant verwalten, Billing, alle Listings, User einladen |
| **admin** | Alle Listings, eBay-Accounts, Templates |
| **member** | Eigene Listings, eigene eBay-Accounts |
| **viewer** | Nur Lesen |

**Prüfung:** Pro Request wird `tenant_id` aus JWT mit Ressourcen-`tenant_id` abgeglichen. Zusätzlich: `user_id` bei member/ viewer.

### 1.4 Verschlüsselung

| Daten | At-Rest | In-Transit |
|-------|---------|------------|
| **DB** | AES-256 (TDE) | TLS 1.3 |
| **S3** | SSE-S3 / SSE-KMS | HTTPS |
| **Sensible Felder** | Feldverschlüsselung (KMS) | - |
| **API** | - | TLS 1.3 |

**Feldverschlüsselung:** `ebay_accounts.access_token_enc`, `ebay_accounts.refresh_token_enc` – Verschlüsselung mit tenant-spezifischem Key aus Vault/KMS.

### 1.5 Secrets Management

| Secret | Speicherort | Rotation |
|--------|-------------|----------|
| DB-Passwörter | Vault / AWS Secrets Manager | 90 Tage |
| API-Keys (eBay, OpenAI) | Vault / Env (K8s Secrets) | Manuell |
| JWT-Signing-Key | Vault, Key-Rotation unterstützt | 365 Tage |
| Encryption Keys | KMS | Automatisch |

### 1.6 Sicherheits-Checkliste (Agent-Review)

| Kriterium | Prüfung |
|-----------|---------|
| **Input-Validierung** | Alle Eingaben gegen Schema validieren, keine direkten DB-Queries aus User-Input |
| **SQL-Injection** | Nur parametrisierte Queries / ORM |
| **XSS** | CSP-Header, Output-Encoding im Frontend |
| **CSRF** | SameSite Cookies, State bei OAuth |
| **Rate Limiting** | Pro IP, pro User, pro Tenant (konfigurierbar) |
| **Sensible Daten** | Keine Tokens/Passwörter in Logs |
| **Audit** | Änderungen an Listings, Credentials, Billing loggen |

---

## 2. Skalierbarkeit

### 2.1 Horizontale Skalierung

| Komponente | Skalierungsstrategie |
|------------|----------------------|
| **API Gateway** | Stateless, mehrere Instanzen hinter LB |
| **Services** | Stateless, HPA (CPU/Memory) |
| **Message Broker** | Cluster-Modus (RabbitMQ Mirrored / Kafka) |
| **PostgreSQL** | Read-Replicas für Lese-Last |
| **Redis** | Cluster-Modus |
| **AI/ML** | Queue-basiert, Worker-Pods skalierbar |

### 2.2 Skalierungs-Trigger (Beispiel HPA)

| Service | Metric | Target | Min/Max Pods |
|---------|--------|--------|--------------|
| Listing | CPU 70% | 70% | 2–20 |
| eBay Integration | Queue-Länge | 100 | 1–10 |
| AI/ML | Queue-Länge | 50 | 1–5 |
| API Gateway | RPS | 1000 | 2–10 |

### 2.3 Caching-Strategie

| Cache-Layer | Inhalt | TTL | Invalidierung |
|-------------|--------|-----|---------------|
| **Redis (Session)** | JWT/Session | 60 Min | Logout |
| **Redis (Listing)** | Listing-Details | 5 Min | Bei Update/Delete |
| **Redis (Rate Limit)** | Request-Counts | 1 Min | Sliding Window |
| **Redis (eBay Categories)** | Kategorie-Baum | 24 Std | Manuell |
| **CDN** | Medien-URLs | 1 Jahr | Bei Replace |

### 2.4 Datenbank-Optimierung

| Maßnahme | Beschreibung |
|---------|--------------|
| **Connection Pooling** | PgBouncer oder App-Pool (max 20/Service) |
| **Read Replicas** | Lese-Operationen (Listings, Reports) auf Replica |
| **Partitioning** | `usage_records` nach `period_start` (Monat) |
| **Archivierung** | Alte `ebay_sync_logs` nach 90 Tagen in Cold Storage |

### 2.5 SaaS-spezifische Skalierung

| Aspekt | Umsetzung |
|--------|-----------|
| **Tenant-Isolation** | Keine Cross-Tenant-Queries, separate Connection-Pools pro Tier (optional) |
| **Ressourcen-Limits** | CPU/Memory Limits pro Namespace (K8s) oder cgroups |
| **Queue-Priorität** | Enterprise-Tenants höhere Priorität (optional) |
| **Kosten-Allokation** | Usage-Tracking pro Tenant für Cost Attribution |

---

## 3. Konsistenz-Prüfung (Architect Agent)

### 3.1 Vorschläge anderer Agents prüfen auf:

| Dimension | Fragen |
|-----------|--------|
| **Konsistenz** | Passt der Vorschlag zu bestehenden Service-Grenzen? Nutzt er die definierten Events/APIs? |
| **Sicherheit** | Werden Credentials/Tokens sicher gehandhabt? Keine neuen Angriffsflächen? |
| **Skalierbarkeit** | Blockiert der Vorschlag horizontale Skalierung? N+1-Queries? |
| **Modularität** | Wird eine neue Abhängigkeit eingeführt, die die Erweiterbarkeit einschränkt? |
| **SaaS-Fähigkeit** | Wird Multi-Tenancy berücksichtigt? Tenant-Isolation gewahrt? |

### 3.2 Abnahme-Checkliste für neue Features

- [ ] Service-Grenze eingehalten (kein direkter DB-Zugriff auf andere Service-Daten)
- [ ] Events statt synchroner Service-Calls wo möglich
- [ ] `tenant_id` / `user_id` in allen neuen Entitäten
- [ ] API-Contract dokumentiert oder erweitert
- [ ] Keine Secrets in Code/Config
- [ ] Rate Limiting berücksichtigt
- [ ] Audit-Log für sensible Aktionen
