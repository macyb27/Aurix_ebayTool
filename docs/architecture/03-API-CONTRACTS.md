# API-Contracts und Schnittstellen

## 1. REST API Konventionen

### 1.1 Basis-URL und Versionierung

```
https://api.aurix-ebay.com/v1/...
```

- **Versionierung:** URL-Pfad (`/v1/`, `/v2/`)
- **Tenant:** Header `X-Tenant-ID: {uuid}` (bei Multi-Tenant)
- **Auth:** `Authorization: Bearer {jwt}`

### 1.2 Standard-Response-Formate

**Erfolg (200/201):**
```json
{
  "data": { ... },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2025-02-13T10:00:00Z"
  }
}
```

**Fehler (4xx/5xx):**
```json
{
  "error": {
    "code": "LISTING_NOT_FOUND",
    "message": "Listing mit ID xyz nicht gefunden",
    "details": { "listingId": "xyz" }
  },
  "meta": {
    "requestId": "req_abc123",
    "timestamp": "2025-02-13T10:00:00Z"
  }
}
```

### 1.3 Pagination

```
GET /listings?page=1&limit=20&sort=-createdAt
```

Response:
```json
{
  "data": [...],
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 150,
      "totalPages": 8
    }
  }
}
```

---

## 2. OpenAPI-ähnliche Contract-Definitionen

### 2.1 Auth Endpoints

| Method | Path | Beschreibung | Request Body |
|--------|------|--------------|--------------|
| POST | `/auth/register` | Registrierung | `RegisterRequest` |
| POST | `/auth/login` | Login | `LoginRequest` |
| POST | `/auth/refresh` | Token erneuern | `RefreshRequest` |
| POST | `/auth/logout` | Logout | - |
| GET | `/auth/me` | Aktueller User | - |

**RegisterRequest:**
```json
{
  "email": "string (required, email)",
  "password": "string (required, min 8)",
  "tenantName": "string (optional)",
  "firstName": "string",
  "lastName": "string"
}
```

**LoginRequest:**
```json
{
  "email": "string",
  "password": "string"
}
```

---

### 2.2 Listing Endpoints

| Method | Path | Beschreibung | Request Body |
|--------|------|--------------|--------------|
| POST | `/listings` | Listing erstellen | `CreateListingRequest` |
| GET | `/listings` | Liste mit Filtern | Query: status, page, limit |
| GET | `/listings/{id}` | Einzelnes Listing | - |
| PUT | `/listings/{id}` | Listing aktualisieren | `UpdateListingRequest` |
| DELETE | `/listings/{id}` | Listing löschen | - |
| POST | `/listings/{id}/publish` | Zur Veröffentlichung einreichen | `PublishRequest` |
| POST | `/listings/{id}/generate-description` | AI-Beschreibung anfordern | - |
| GET | `/listings/templates` | Vorlagen auflisten | - |

**CreateListingRequest:**
```json
{
  "templateId": "uuid (optional)",
  "vehicle": {
    "make": "string (required)",
    "model": "string (required)",
    "year": "number (required)",
    "mileage": "number",
    "fuelType": "string",
    "transmission": "string",
    "condition": "string",
    "vin": "string",
    "customAttributes": {}
  },
  "title": "string (optional, AI-generierbar)",
  "description": "string (optional, AI-generierbar)",
  "price": { "amount": "number", "currency": "EUR" },
  "mediaIds": ["uuid"],
  "categoryId": "string (eBay Kategorie)"
}
```

**PublishRequest:**
```json
{
  "ebayAccountId": "uuid",
  "duration": "GTC|DAYS_7|DAYS_30",
  "scheduledStartTime": "ISO8601 (optional)"
}
```

---

### 2.3 eBay Integration Endpoints

| Method | Path | Beschreibung | Request Body |
|--------|------|--------------|--------------|
| GET | `/ebay/accounts` | Verbundene eBay-Accounts | - |
| POST | `/ebay/accounts/connect` | OAuth-Flow starten | `ConnectRequest` |
| DELETE | `/ebay/accounts/{id}` | Account trennen | - |
| GET | `/ebay/categories` | Kategorien suchen | Query: q, parentId |
| GET | `/ebay/sync-status` | Sync-Status | - |

**ConnectRequest:**
```json
{
  "redirectUri": "string",
  "state": "string (CSRF)"
}
```

---

### 2.4 Media Endpoints

| Method | Path | Beschreibung | Request Body |
|--------|------|--------------|--------------|
| POST | `/media/upload` | Presigned URL anfordern | `UploadRequest` |
| POST | `/media/upload/complete` | Upload bestätigen | `CompleteUploadRequest` |
| GET | `/media/{id}` | Metadaten abrufen | - |
| DELETE | `/media/{id}` | Medien löschen | - |

**UploadRequest:**
```json
{
  "fileName": "string",
  "contentType": "image/jpeg",
  "size": "number",
  "listingId": "uuid (optional)"
}
```

**Response (Presigned URL):**
```json
{
  "uploadId": "uuid",
  "uploadUrl": "string (presigned URL)",
  "expiresAt": "ISO8601"
}
```

---

### 2.5 Billing Endpoints

| Method | Path | Beschreibung |
|--------|------|--------------|
| GET | `/billing/subscription` | Aktuelles Abo |
| GET | `/billing/usage` | Nutzungsstatistik |
| POST | `/billing/checkout` | Checkout-Session (Stripe) |
| GET | `/billing/invoices` | Rechnungen |

---

## 3. Event-Contracts (Message Broker)

### 3.1 Event-Topics

| Topic | Producer | Consumer | Beschreibung |
|-------|----------|----------|--------------|
| `listings` | Listing, User | Listing, AI, eBay, Billing | Listing-Lifecycle |
| `users` | User | Billing, Notification | User-Events |
| `ebay-sync` | eBay Integration | Listing, Notification | eBay-Sync-Status |
| `ai-jobs` | Listing, AI | AI | AI-Aufgaben |
| `notifications` | Alle | Notification | Benachrichtigungen |

### 3.2 Event-Struktur (Standard)

```json
{
  "eventId": "uuid",
  "eventType": "listing.publish.requested",
  "eventVersion": "1.0",
  "timestamp": "2025-02-13T10:00:00Z",
  "source": "listing-service",
  "tenantId": "uuid",
  "userId": "uuid",
  "correlationId": "uuid",
  "payload": { ... },
  "metadata": {}
}
```

### 3.3 Event-Payloads (JSON Schema)

**listing.created**
```json
{
  "listingId": "uuid",
  "tenantId": "uuid",
  "userId": "uuid",
  "status": "draft",
  "vehicleMake": "string",
  "vehicleModel": "string"
}
```

**listing.publish.requested**
```json
{
  "listingId": "uuid",
  "ebayAccountId": "uuid",
  "duration": "GTC|DAYS_7|DAYS_30",
  "scheduledStartTime": "ISO8601 (optional)"
}
```

**ai.description.requested**
```json
{
  "jobId": "uuid",
  "listingId": "uuid",
  "vehicleData": { ... },
  "language": "de"
}
```

**ai.description.ready**
```json
{
  "jobId": "uuid",
  "listingId": "uuid",
  "title": "string",
  "description": "string",
  "keywords": ["string"]
}
```

**ebay.sync.completed**
```json
{
  "listingId": "uuid",
  "ebayItemId": "string",
  "status": "active",
  "url": "string"
}
```

**ebay.sync.failed**
```json
{
  "listingId": "uuid",
  "errorCode": "string",
  "errorMessage": "string",
  "retryable": "boolean"
}
```

---

## 4. Webhook-Contracts (Outbound)

Für externe Systeme (z.B. ERP):

| Event | URL-Parameter | Payload |
|-------|---------------|---------|
| `listing.published` | - | `ListingPublishedPayload` |
| `listing.sold` | - | `ListingSoldPayload` |
| `sync.failed` | - | `SyncFailedPayload` |

**Signatur:** `X-Aurix-Signature: <HMAC-SHA256(payload, secret)>`

---

## 5. Fehlercodes (Standard)

| Code | HTTP | Beschreibung |
|------|------|--------------|
| `UNAUTHORIZED` | 401 | Token fehlt/ungültig |
| `FORBIDDEN` | 403 | Keine Berechtigung |
| `NOT_FOUND` | 404 | Ressource nicht gefunden |
| `VALIDATION_ERROR` | 400 | Request-Validierung fehlgeschlagen |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate Limit überschritten |
| `SUBSCRIPTION_REQUIRED` | 402 | Upgrade erforderlich |
| `EBAY_API_ERROR` | 502 | eBay API Fehler |
| `INTERNAL_ERROR` | 500 | Serverfehler |
