# API-Contracts und Schnittstellen

## 1. Konventionen

### 1.1 Allgemeine Regeln
- **Base URL**: `https://api.{tenant}.ebay-tool.com/v1` (oder Subdomain-Routing)
- **Content-Type**: `application/json`
- **Auth**: `Authorization: Bearer <JWT>`
- **Tenant**: `X-Tenant-Id: <uuid>` (bei Multi-Tenant)
- **Request-ID**: `X-Request-Id: <uuid>` (für Tracing)

### 1.2 Fehlerformat (RFC 7807)

```json
{
  "type": "https://api.ebay-tool.com/errors/validation",
  "title": "Validation Error",
  "status": 400,
  "detail": "Invalid listing data",
  "instance": "/v1/listings",
  "traceId": "abc-123",
  "errors": [
    {
      "field": "title",
      "message": "Title must be between 10 and 80 characters"
    }
  ]
}
```

### 1.3 Pagination

```json
{
  "data": [...],
  "meta": {
    "page": 1,
    "perPage": 20,
    "total": 150,
    "totalPages": 8
  },
  "links": {
    "self": "/v1/listings?page=1",
    "next": "/v1/listings?page=2",
    "prev": null
  }
}
```

---

## 2. Auth Service – API Contract

### POST /auth/login

**Request:**
```json
{
  "email": "string",
  "password": "string",
  "tenantId": "uuid (optional)"
}
```

**Response 200:**
```json
{
  "accessToken": "string",
  "refreshToken": "string",
  "expiresIn": 3600,
  "tokenType": "Bearer",
  "user": {
    "id": "uuid",
    "email": "string",
    "roles": ["string"],
    "tenantId": "uuid"
  }
}
```

### POST /auth/refresh

**Request:**
```json
{
  "refreshToken": "string"
}
```

**Response 200:** Wie Login-Response

### GET /auth/me

**Headers:** `Authorization: Bearer <token>`

**Response 200:**
```json
{
  "id": "uuid",
  "email": "string",
  "tenantId": "uuid",
  "roles": ["admin", "seller"],
  "permissions": ["listings:write", "inventory:read"]
}
```

---

## 3. Tenant Service – API Contract

### GET /tenants/:id

**Response 200:**
```json
{
  "id": "uuid",
  "name": "string",
  "slug": "string",
  "plan": "starter|professional|enterprise",
  "subscriptionStatus": "active|past_due|canceled",
  "limits": {
    "listingsPerMonth": 100,
    "productsMax": 1000,
    "aiCallsPerMonth": 500
  },
  "usage": {
    "listingsThisMonth": 45,
    "aiCallsThisMonth": 120
  }
}
```

### POST /tenants/:id/check-limit

**Request:**
```json
{
  "resource": "listings|products|aiCalls",
  "increment": 1
}
```

**Response 200:**
```json
{
  "allowed": true,
  "remaining": 55,
  "limit": 100
}
```

---

## 4. Inventory Service – API Contract

### GET /products

**Query:** `?page=1&perPage=20&search=&categoryId=`

**Response 200:** Paginated

```json
{
  "data": [
    {
      "id": "uuid",
      "sku": "string",
      "name": "string",
      "description": "string",
      "categoryId": "uuid",
      "variants": [
        {
          "id": "uuid",
          "sku": "string",
          "attributes": {"size": "M", "color": "blue"},
          "stock": 10,
          "price": 29.99
        }
      ],
      "images": ["url1", "url2"],
      "createdAt": "ISO8601",
      "updatedAt": "ISO8601"
    }
  ],
  "meta": {...},
  "links": {...}
}
```

### POST /products

**Request:**
```json
{
  "sku": "string",
  "name": "string",
  "description": "string",
  "categoryId": "uuid",
  "variants": [
    {
      "sku": "string",
      "attributes": {"size": "M"},
      "stock": 0,
      "price": 0
    }
  ],
  "images": ["url"]
}
```

### PATCH /products/:id/stock

**Request:**
```json
{
  "variantId": "uuid",
  "quantity": 5,
  "reason": "restock|sale|adjustment"
}
```

---

## 5. Listing Service – API Contract

### POST /listings

**Request:**
```json
{
  "productId": "uuid",
  "templateId": "uuid (optional)",
  "title": "string",
  "description": "string",
  "price": 29.99,
  "quantity": 10,
  "categoryId": "string (eBay category)",
  "condition": "new|used|refurbished",
  "images": ["url"],
  "duration": "GTC|Days_3|Days_5|Days_7",
  "paymentMethods": ["PayPal", "CreditCard"],
  "shippingOptions": [
    {
      "type": "flat",
      "cost": 4.99,
      "domesticOnly": true
    }
  ]
}
```

**Response 201:**
```json
{
  "id": "uuid",
  "status": "draft",
  "productId": "uuid",
  "createdAt": "ISO8601",
  "workflow": {
    "currentStep": "draft",
    "nextSteps": ["review", "publish"]
  }
}
```

### POST /listings/:id/generate-ai

**Request:**
```json
{
  "fields": ["title", "description", "category"],
  "productId": "uuid"
}
```

**Response 202:**
```json
{
  "jobId": "uuid",
  "status": "pending",
  "estimatedCompletion": "ISO8601"
}
```

### POST /listings/:id/approve

**Response 200:**
```json
{
  "id": "uuid",
  "status": "approved",
  "readyForPublish": true
}
```

### POST /listings/:id/publish

**Response 202:**
```json
{
  "id": "uuid",
  "status": "publishing",
  "syncJobId": "uuid"
}
```

---

## 6. AI Service – API Contract

### POST /ai/generate-description

**Request:**
```json
{
  "productName": "string",
  "productAttributes": {"brand": "X", "material": "Y"},
  "images": ["url"],
  "targetLength": "short|medium|long",
  "language": "de"
}
```

**Response 200 (sync) / 202 (async):**
```json
{
  "jobId": "uuid",
  "result": {
    "title": "string",
    "description": "string",
    "suggestedCategory": "string",
    "tags": ["string"]
  },
  "status": "completed"
}
```

### GET /ai/jobs/:id

**Response 200:**
```json
{
  "id": "uuid",
  "status": "pending|processing|completed|failed",
  "result": {...},
  "error": "string (if failed)",
  "createdAt": "ISO8601",
  "completedAt": "ISO8601"
}
```

---

## 7. Sync Service – API Contract

### POST /sync/publish

**Request:**
```json
{
  "listingId": "uuid",
  "tenantId": "uuid",
  "ebayAccountId": "uuid"
}
```

**Response 202:**
```json
{
  "syncJobId": "uuid",
  "status": "queued",
  "listingId": "uuid"
}
```

### GET /sync/status/:listingId

**Response 200:**
```json
{
  "listingId": "uuid",
  "status": "queued|publishing|published|failed",
  "ebayItemId": "string (if published)",
  "ebayUrl": "string",
  "lastError": "string (if failed)",
  "updatedAt": "ISO8601"
}
```

---

## 8. Event-Contracts (CloudEvents 1.0)

### Event: listing.draft.created

```json
{
  "specversion": "1.0",
  "type": "listing.draft.created",
  "source": "listing-service",
  "id": "uuid",
  "time": "ISO8601",
  "datacontenttype": "application/json",
  "data": {
    "listingId": "uuid",
    "tenantId": "uuid",
    "productId": "uuid",
    "title": "string",
    "description": "string",
    "images": ["url"],
    "requestedFields": ["title", "description"]
  }
}
```

### Event: ai.job.completed

```json
{
  "specversion": "1.0",
  "type": "ai.job.completed",
  "source": "ai-service",
  "id": "uuid",
  "time": "ISO8601",
  "data": {
    "jobId": "uuid",
    "listingId": "uuid",
    "result": {
      "title": "string",
      "description": "string",
      "suggestedCategory": "string",
      "tags": ["string"]
    }
  }
}
```

### Event: listing.approved

```json
{
  "specversion": "1.0",
  "type": "listing.approved",
  "source": "listing-service",
  "id": "uuid",
  "time": "ISO8601",
  "data": {
    "listingId": "uuid",
    "tenantId": "uuid",
    "ebayAccountId": "uuid",
    "listingPayload": {...}
  }
}
```

### Event: inventory.synced

```json
{
  "specversion": "1.0",
  "type": "inventory.synced",
  "source": "inventory-service",
  "id": "uuid",
  "time": "ISO8601",
  "data": {
    "productId": "uuid",
    "variantId": "uuid",
    "newStock": 10,
    "previousStock": 8
  }
}
```

### Event: sync.completed

```json
{
  "specversion": "1.0",
  "type": "sync.completed",
  "source": "sync-service",
  "id": "uuid",
  "time": "ISO8601",
  "data": {
    "listingId": "uuid",
    "ebayItemId": "string",
    "status": "success|partial|failed",
    "ebayUrl": "string"
  }
}
```

---

## 9. OpenAPI-Spezifikation (Referenz)

Die vollständige OpenAPI 3.0-Spezifikation liegt unter:
- `contracts/openapi/auth.yaml`
- `contracts/openapi/tenant.yaml`
- `contracts/openapi/inventory.yaml`
- `contracts/openapi/listing.yaml`
- `contracts/openapi/ai.yaml`
- `contracts/openapi/sync.yaml`

Diese können mit Swagger UI oder Redoc visualisiert werden.
