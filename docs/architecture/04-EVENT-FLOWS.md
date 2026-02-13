# Event-Flows und Prozess-Sequenzen

## 1. Event-Architektur

### 1.1 Event-Bus Topologie

```mermaid
graph TB
    subgraph "Exchanges"
        EX_LISTING[listing.*]
        EX_AI[ai.*]
        EX_INVENTORY[inventory.*]
        EX_SYNC[sync.*]
    end
    
    subgraph "Publishers"
        LS[Listing Service]
        AIS[AI Service]
        INS[Inventory Service]
        SS[Sync Service]
    end
    
    subgraph "Consumers / Queues"
        Q_AI[ai-service.queue]
        Q_SYNC[sync-service.queue]
        Q_LISTING[listing-service.queue]
        Q_INVENTORY[inventory-service.queue]
    end
    
    LS -->|listing.draft.created| EX_LISTING
    LS -->|listing.approved| EX_LISTING
    AIS -->|ai.job.completed| EX_AI
    INS -->|inventory.synced| EX_INVENTORY
    SS -->|sync.completed| EX_SYNC
    
    EX_LISTING --> Q_AI
    EX_LISTING --> Q_SYNC
    EX_AI --> Q_LISTING
    EX_INVENTORY --> Q_LISTING
    EX_SYNC --> Q_LISTING
```

### 1.2 Event-Typen und Routing

| Event | Publisher | Consumer(s) | Queue |
|-------|-----------|-------------|-------|
| `listing.draft.created` | Listing Service | AI Service | ai.incoming |
| `listing.approved` | Listing Service | Sync Service | sync.publish |
| `ai.job.completed` | AI Service | Listing Service | listing.ai-results |
| `inventory.synced` | Inventory Service | Listing Service | listing.inventory-updates |
| `sync.completed` | Sync Service | Listing Service | listing.sync-results |
| `sync.failed` | Sync Service | Listing Service | listing.sync-results |
| `tenant.plan.changed` | Tenant Service | Alle (broadcast) | *.tenant-updates |

---

## 2. Flow: Listing mit AI-Generierung erstellen

```mermaid
sequenceDiagram
    participant U as User/Frontend
    participant GW as API Gateway
    participant LS as Listing Service
    participant MQ as Message Queue
    participant AI as AI Service
    participant DB as Database
    
    U->>GW: POST /listings (Draft)
    GW->>LS: Create Listing
    LS->>DB: Persist Draft
    LS-->>U: 201 { listingId }
    
    U->>GW: POST /listings/:id/generate-ai
    GW->>LS: Trigger AI
    LS->>LS: Validate, create AI Job ref
    LS->>MQ: Publish listing.draft.created
    LS-->>U: 202 { jobId }
    
    MQ->>AI: listing.draft.created
    AI->>AI: Generate (LLM)
    AI->>DB: Store result
    AI->>MQ: Publish ai.job.completed
    
    MQ->>LS: ai.job.completed
    LS->>DB: Update listing (title, description)
    LS->>DB: Mark AI job done
    
    Note over U,DB: Optional: WebSocket/Polling für Live-Update
    U->>GW: GET /ai/jobs/:id
    GW->>AI: Get Job Status
    AI-->>U: 200 { result }
```

---

## 3. Flow: Listing zur eBay veröffentlichen

```mermaid
sequenceDiagram
    participant U as User
    participant GW as API Gateway
    participant LS as Listing Service
    participant TS as Tenant Service
    participant MQ as Message Queue
    participant SS as Sync Service
    participant EA as eBay Adapter
    participant eBay as eBay API
    
    U->>GW: POST /listings/:id/approve
    GW->>LS: Approve
    LS->>TS: Check limit (listings)
    TS-->>LS: OK
    LS->>LS: Update status = approved
    LS-->>U: 200
    
    U->>GW: POST /listings/:id/publish
    GW->>LS: Publish
    LS->>LS: Validate (complete data)
    LS->>MQ: Publish listing.approved
    LS-->>U: 202 { syncJobId }
    
    MQ->>SS: listing.approved
    SS->>SS: Load listing + product
    SS->>EA: Create/Update eBay Listing
    EA->>eBay: POST /sell/inventory/v1/offer
    eBay-->>EA: offerId
    EA->>eBay: POST /sell/inventory/v1/offer/offerId/publish
    eBay-->>EA: listingId
    EA-->>SS: Success
    
    SS->>SS: Store ebay_item_id
    SS->>MQ: Publish sync.completed
    
    MQ->>LS: sync.completed
    LS->>LS: Update listing status = published
```

---

## 4. Flow: Bestands-Synchronisation (eBay → System)

```mermaid
sequenceDiagram
    participant eBay as eBay Webhook
    participant GW as API Gateway
    participant SS as Sync Service
    participant MQ as Message Queue
    participant INS as Inventory Service
    participant LS as Listing Service
    
    eBay->>GW: POST /webhooks/ebay (sale/order)
    GW->>SS: Handle Webhook
    SS->>SS: Verify Signature
    SS->>eBay: Fetch Order Details (API)
    eBay-->>SS: Order with line items
    
    SS->>SS: Map ebay_item_id → listing_id → product_id
    
    alt Stock Update
        SS->>MQ: Publish inventory.update.requested
        MQ->>INS: inventory.update.requested
        INS->>INS: Decrement stock
        INS->>MQ: Publish inventory.synced
        MQ->>LS: inventory.synced
        LS->>LS: Invalidate cache / notify
    end
```

---

## 5. Flow: Fehlerbehandlung und Retry

```mermaid
stateDiagram-v2
    [*] --> Queued: Publish Event
    Queued --> Processing: Consumer picks up
    Processing --> Completed: Success
    Processing --> Failed: Error (no retry)
    Processing --> Retrying: Error (retryable)
    
    Retrying --> Queued: Back to queue (delay)
    Retrying --> DeadLetter: Max retries exceeded
    
    DeadLetter --> [*]: Manual intervention
    Completed --> [*]
    Failed --> [*]
```

### Retry-Policy
| Fehlertyp | Retries | Backoff |
|-----------|---------|---------|
| eBay API 5xx | 5 | Exponential (1s, 2s, 4s, 8s, 16s) |
| eBay Rate Limit 429 | 3 | Fixed 60s |
| AI Provider Timeout | 2 | Fixed 30s |
| Validation Error | 0 | - |
| DB Deadlock | 3 | Exponential |

### Dead-Letter-Queue
- Events in DLQ werden geloggt und für manuelle Prüfung bereitgestellt
- Alert an Ops bei DLQ-Einträgen
- Kein automatisches Re-Queue ohne Review

---

## 6. Flow: Multi-Tenant-Isolation

```mermaid
sequenceDiagram
    participant U as User
    participant GW as API Gateway
    participant AUTH as Auth Service
    participant SVC as Any Service
    
    U->>GW: Request + JWT
    GW->>AUTH: Validate JWT
    AUTH-->>GW: { userId, tenantId, roles }
    
    GW->>GW: Inject X-Tenant-Id
    GW->>SVC: Request + X-Tenant-Id
    
    SVC->>SVC: Assert tenant_id in query
    SVC->>SVC: WHERE tenant_id = :tenantId
    SVC-->>GW: Response
    GW-->>U: Response
```

**Regel:** Jede Datenbankabfrage MUSS `tenant_id` im WHERE-Clause enthalten (außer systemweite Abfragen).

---

## 7. Idempotenz

Für kritische Events (z.B. `listing.approved` → Publish):

| Mechanismus | Implementierung |
|-------------|-----------------|
| **Idempotency-Key** | Client sendet `X-Idempotency-Key: uuid` |
| **Storage** | Redis: `idempotency:{key}` → Response (TTL 24h) |
| **Duplicate** | Bei gleichem Key: Return cached Response, kein erneuter Publish |
| **Event-ID** | CloudEvents `id` wird in DB gespeichert, Duplikate ignoriert |

---

## 8. Event-Schema-Versionierung

Bei Breaking Changes:
- **Neue Felder**: Additiv, Consumer ignorieren unbekannte Felder
- **Entfernte Felder**: Deprecation-Period, dann neues Event `listing.draft.created.v2`
- **Routing**: Alte und neue Events parallel bis Migration abgeschlossen
