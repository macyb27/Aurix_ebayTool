# Service-Grenzen und Abhängigkeiten

## 1. Service-Übersicht

| Service | Verantwortung | Port (Intern) | Abhängigkeiten |
|---------|---------------|---------------|----------------|
| **User Service** | Auth, Profile, Tenant, Berechtigungen | 3001 | PostgreSQL, Redis |
| **Listing Service** | Listing CRUD, Templates, Workflows | 3002 | PostgreSQL, Redis, Event Bus |
| **eBay Integration Service** | eBay API, OAuth, Sync, Rate-Limiting | 3003 | PostgreSQL, Redis, eBay API |
| **AI/ML Service** | Beschreibungsgenerierung, Bildanalyse | 3004 | Vector DB, OpenAI/LLM, S3 |
| **Billing Service** | Subscriptions, Usage, Invoicing | 3005 | PostgreSQL, Payment Provider |
| **Notification Service** | E-Mail, Push, Webhooks | 3006 | SMTP, Event Bus |
| **Media Service** | Upload, Resize, CDN-URLs | 3007 | S3, Redis |

---

## 2. Service-Detail-Spezifikationen

### 2.1 User Service

**Domain:** Identity & Access Management, Multi-Tenancy

| Aspekt | Spezifikation |
|--------|---------------|
| **Eingänge** | REST API, Events: `user.created`, `tenant.invited` |
| **Ausgänge** | Events: `user.registered`, `user.updated`, `session.created` |
| **Daten** | users, tenants, roles, permissions, sessions |
| **Externe** | OAuth2 Provider (Google, Microsoft), SMTP (via Notification) |
| **Nicht zuständig** | Listing-Logik, eBay-Credentials (nur Referenz) |

**Schnittstellen:**
- `POST /auth/register` - Registrierung
- `POST /auth/login` - Login (JWT)
- `GET /users/me` - Profil
- `GET /tenants/{id}` - Tenant-Info
- `POST /tenants/{id}/invite` - Einladung

---

### 2.2 Listing Service

**Domain:** Kern-Domain - Fahrzeuginserate

| Aspekt | Spezifikation |
|--------|---------------|
| **Eingänge** | REST API, Events: `ai.description.ready`, `ebay.sync.completed` |
| **Ausgänge** | Events: `listing.created`, `listing.updated`, `listing.publish.requested` |
| **Daten** | listings, listing_templates, listing_workflows, drafts |
| **Externe** | AI Service (async), eBay Integration (async via Events) |
| **Nicht zuständig** | eBay API-Aufrufe, Zahlungsabwicklung |

**Schnittstellen:**
- `POST /listings` - Listing erstellen
- `GET /listings` - Liste (Filter, Pagination)
- `PUT /listings/{id}` - Aktualisieren
- `POST /listings/{id}/publish` - Zur Veröffentlichung einreichen
- `GET /listings/templates` - Vorlagen

---

### 2.3 eBay Integration Service

**Domain:** eBay API-Anbindung, OAuth, Sync

| Aspekt | Spezifikation |
|--------|---------------|
| **Eingänge** | Events: `listing.publish.requested`, `ebay.credentials.updated` |
| **Ausgänge** | Events: `ebay.sync.completed`, `ebay.sync.failed`, `ebay.rate_limit.hit` |
| **Daten** | ebay_credentials (encrypted), ebay_categories, sync_logs |
| **Externe** | eBay Trading API, eBay Inventory API, eBay OAuth |
| **Nicht zuständig** | Listing-Business-Logik, AI |

**Besonderheiten:**
- **Rate Limiting:** Eigenes Throttling pro eBay-Account
- **Retry:** Exponential Backoff bei 5xx
- **Webhooks:** eBay-Notifications empfangen (separater Endpoint)

---

### 2.4 AI/ML Service

**Domain:** KI-gestützte Inhaltserstellung

| Aspekt | Spezifikation |
|--------|---------------|
| **Eingänge** | Events: `listing.draft.created`, `ai.description.requested` |
| **Ausgänge** | Events: `ai.description.ready`, `ai.image.analyzed` |
| **Daten** | ai_jobs, embeddings (Vector DB) |
| **Externe** | OpenAI API, Azure OpenAI, S3 (Bilder) |
| **Nicht zuständig** | eBay-Publishing, User-Management |

**Funktionen:**
- Beschreibungsgenerierung aus Fahrzeugdaten
- SEO-Optimierung
- Bild-Tagging (optional)
- Übersetzung (optional)

---

### 2.5 Billing Service

**Domain:** Abrechnung, Subscriptions

| Aspekt | Spezifikation |
|--------|---------------|
| **Eingänge** | Events: `listing.published`, `user.registered` |
| **Ausgänge** | Events: `billing.invoice.created`, `subscription.upgraded` |
| **Daten** | subscriptions, invoices, usage_records |
| **Externe** | Stripe, PayPal, Rechnungsstellung |
| **Nicht zuständig** | Feature-Freischaltung (User Service prüft) |

---

### 2.6 Notification Service

**Domain:** Benachrichtigungen

| Aspekt | Spezifikation |
|--------|---------------|
| **Eingänge** | Events: `notification.requested`, `listing.published` |
| **Ausgänge** | Keine (Side-Effect) |
| **Daten** | notification_preferences, notification_logs |
| **Externe** | SMTP, SendGrid, Firebase (Push), Webhook-URLs |
| **Nicht zuständig** | Business-Logik |

---

### 2.7 Media Service

**Domain:** Dateiverwaltung

| Aspekt | Spezifikation |
|--------|---------------|
| **Eingänge** | REST API (Upload), Events: `media.resize.requested` |
| **Ausgänge** | Events: `media.uploaded`, `media.resized` |
| **Daten** | media_assets (Metadaten), S3-Bucket |
| **Externe** | S3/MinIO, Image-Processing (Sharp, ImageMagick) |
| **Nicht zuständig** | Listing-Zuordnung (Listing Service) |

---

## 3. Abhängigkeitsmatrix

```
                    User  Listing  eBay  AI   Billing  Notif  Media
User Service        -     -        -     -    -        -      -
Listing Service     R     -        E     E    -        -      R
eBay Integration    R     E        -     -    -        -      -
AI/ML Service       R     E        -     -    -        -      R
Billing Service     R     E        -     -    -        -      -
Notification        R     E        E     -    E        -      -
Media Service       R     E        -     -    -        -      -

R = Read (sync API call oder Cache)
E = Event (async über Message Broker)
```

**Regel:** Kein Service ruft einen anderen Service synchron für Kern-Business-Logik auf. Kommunikation primär über Events.

---

## 4. Service-zu-Datenbank-Mapping

| Service | Primäre DB | Cache | Externe Stores |
|---------|------------|-------|----------------|
| User | PostgreSQL (users, tenants) | Redis (sessions) | - |
| Listing | PostgreSQL (listings) | Redis (drafts) | - |
| eBay Integration | PostgreSQL (credentials, sync_logs) | Redis (rate_limit) | eBay API |
| AI/ML | PostgreSQL (jobs) | - | Vector DB, S3 |
| Billing | PostgreSQL (subscriptions) | Redis (usage_cache) | Stripe |
| Notification | PostgreSQL (prefs, logs) | - | SMTP |
| Media | PostgreSQL (media_assets) | Redis (upload_tokens) | S3 |

---

## 5. Erweiterbarkeitspunkte

| Erweiterung | Betroffener Service | Mechanismus |
|-------------|---------------------|-------------|
| Neuer Marketplace (z.B. Mobile.de) | Neuer "Marketplace Integration Service" | Gleiche Events wie eBay (`listing.publish.requested`) |
| Weitere AI-Provider | AI/ML Service | Strategy Pattern, Config-basiert |
| Neue Zahlungsmethode | Billing Service | Payment-Adapter-Interface |
| Webhook-Formate | Notification Service | Template-basierte Payloads |
| Listing-Typen (z.B. Boote) | Listing Service | Polymorphes Schema, Category-Config |
