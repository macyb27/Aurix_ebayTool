# Event-Flows und Prozessabläufe

## 1. Event-Architektur-Übersicht

```
                    ┌─────────────────────────────────────────┐
                    │           MESSAGE BROKER                 │
                    │  Topics: listings | ebay-sync | ai-jobs  │
                    └─────────────────┬───────────────────────┘
                                      │
    ┌─────────────┐    ┌──────────────┼──────────────┐    ┌─────────────┐
    │   User      │    │   Listing    │   eBay       │    │   AI/ML     │
    │   Service   │    │   Service    │   Integration│    │   Service   │
    └──────┬──────┘    └──────┬──────┴──────┬───────┘    └──────┬──────┘
           │                  │             │                   │
           │  publish         │  publish    │  consume          │  consume
           │  requested       │  requested  │  publish         │  requested
           └──────────────────┴─────────────┴───────────────────┘
```

---

## 2. Flow 1: Listing erstellen und AI-Beschreibung generieren

```
User          Listing Svc       Event Bus        AI/ML Svc       Media Svc
  │                │                 │                 │              │
  │ POST /listings │                 │                 │              │
  │──────────────>│                 │                 │              │
  │                │ listing.created │                 │              │
  │                │────────────────>│                 │              │
  │                │                 │ ai.description  │              │
  │                │                 │ .requested      │              │
  │                │                 │────────────────>│              │
  │  201 Created   │                 │                 │              │
  │<───────────────│                 │                 │              │
  │                │                 │                 │ (LLM Call)   │
  │                │                 │ ai.description  │              │
  │                │                 │ .ready          │              │
  │                │<────────────────│<────────────────│              │
  │                │ UPDATE listing  │                 │              │
  │                │ (title, desc)   │                 │              │
  │                │                 │                 │              │
```

**Sequenz:**
1. User erstellt Listing (Draft) via REST
2. Listing Service persistiert, publiziert `listing.created`
3. AI/ML Service konsumiert (optional: nur wenn description leer), publiziert `ai.description.requested` (intern) oder verarbeitet direkt
4. AI generiert Beschreibung, publiziert `ai.description.ready`
5. Listing Service aktualisiert Listing mit generierten Inhalten

---

## 3. Flow 2: Listing auf eBay veröffentlichen

```
User          Listing Svc       Event Bus        eBay Integration    Notification
  │                │                 │                 │                 │
  │ POST /publish  │                 │                 │                 │
  │──────────────>│                 │                 │                 │
  │                │ listing.publish │                 │                 │
  │                │ .requested      │                 │                 │
  │                │────────────────>│────────────────>│                 │
  │  202 Accepted  │                 │                 │                 │
  │<───────────────│                 │                 │                 │
  │                │                 │                 │ eBay API Call   │
  │                │                 │                 │ (AddItem/...)   │
  │                │                 │ ebay.sync       │                 │
  │                │                 │ .completed      │                 │
  │                │<────────────────│<────────────────│                 │
  │                │ UPDATE listing  │                 │                 │
  │                │ (ebay_item_id)  │                 │                 │
  │                │                 │ listing.published│                │
  │                │                 │────────────────>│────────────────>│
  │                │                 │                 │                 │ E-Mail
```

**Sequenz:**
1. User klickt "Veröffentlichen"
2. Listing Service validiert, setzt Status `publishing`, publiziert `listing.publish.requested`
3. eBay Integration Service holt Credentials, ruft eBay API auf
4. Bei Erfolg: `ebay.sync.completed` → Listing Service aktualisiert, Billing zählt Usage
5. Bei Fehler: `ebay.sync.failed` → Listing Service setzt Status `failed`, Notification sendet Alert

---

## 4. Flow 3: eBay OAuth-Verbindung herstellen

```
User          Frontend         API Gateway      User Svc       eBay Integration
  │                │                 │               │                 │
  │ Connect eBay   │                 │               │                 │
  │──────────────>│                 │               │                 │
  │                │ GET /ebay/connect│               │                 │
  │                │────────────────>│               │                 │
  │                │                 │               │ Redirect URL    │
  │                │                 │               │ + state (CSRF)   │
  │                │                 │               │<────────────────│
  │  Redirect      │                 │               │                 │
  │  to eBay       │<────────────────│               │                 │
  │<───────────────│                 │               │                 │
  │                │                 │               │                 │
  │  [User auth auf eBay]            │               │                 │
  │                │                 │               │                 │
  │  Callback      │                 │               │                 │
  │  ?code=...     │                 │               │                 │
  │──────────────>│ POST /ebay/callback             │                 │
  │                │────────────────>│──────────────>│────────────────>│
  │                │                 │               │                 │ Token Exchange
  │                │                 │               │                 │ (eBay API)
  │                │                 │               │                 │ Store encrypted
  │  200 OK        │                 │               │                 │
  │<───────────────│<────────────────│<──────────────│<────────────────│
```

**Hinweis:** OAuth-Callback kann direkt am eBay Integration Service hängen oder über API Gateway geroutet werden.

---

## 5. Flow 4: eBay-Webhook (Listing verkauft)

```
eBay           API Gateway      eBay Integration    Event Bus       Listing/Billing
  │                 │                 │                 │                 │
  │ POST /webhooks  │                 │                 │                 │
  │ (ItemSold)      │                 │                 │                 │
  │────────────────>│────────────────>│                 │                 │
  │                 │                 │ Verify Sig      │                 │
  │                 │                 │ listing.sold    │                 │
  │                 │                 │────────────────>│────────────────>│
  │  200 OK         │                 │                 │                 │ Update status
  │<────────────────│<────────────────│                 │                 │ Billing event
```

---

## 6. Flow 5: Subscription-Upgrade und Feature-Freischaltung

```
User          Billing Svc      Event Bus       User Svc       Listing Svc
  │                │                 │               │                 │
  │ Checkout       │                 │               │                 │
  │──────────────>│                 │               │                 │
  │                │ Stripe Session  │               │                 │
  │                │ subscription    │               │                 │
  │                │ .upgraded       │               │                 │
  │                │────────────────>│               │                 │
  │                │                 │──────────────>│ Update plan      │
  │                │                 │               │ (Cache inval.)   │
  │                │                 │               │                 │
  │                │                 │──────────────>│ Listing limits   │
  │                │                 │               │ erweitert        │
```

---

## 7. Event-Retry und Dead-Letter

| Konfiguration | Wert | Beschreibung |
|---------------|------|--------------|
| **Max Retries** | 3 | Pro Event |
| **Backoff** | Exponential (1s, 2s, 4s) | |
| **DLQ** | `dlq.{topic}` | Nach 3 Fehlern |
| **Alert** | Bei DLQ-Eintrag | PagerDuty/Slack |
| **Idempotenz** | `eventId` als Key | Doppelverarbeitung vermeiden |

---

## 8. Korrelations-ID (Tracing)

Jeder Request erhält eine `correlationId` (UUID). Diese wird:
- Im Response-Header `X-Correlation-ID` zurückgegeben
- In alle Events weitergegeben
- In Logs und Traces durchgereicht

**Beispiel:** Ein Publish-Request kann über `correlationId` vom initialen API-Call bis zum eBay-API-Call und zurück verfolgt werden.
