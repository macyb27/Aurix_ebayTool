# Datenbankschema

## 1. Übersicht

| Schema/Bereich | Service | Tabellen |
|----------------|---------|----------|
| `identity` | User | users, tenants, roles, permissions, sessions |
| `listings` | Listing | listings, listing_templates, listing_workflows |
| `ebay` | eBay Integration | ebay_accounts, ebay_sync_logs, ebay_categories_cache |
| `ai` | AI/ML | ai_jobs, ai_embeddings (Vector) |
| `billing` | Billing | subscriptions, invoices, usage_records |
| `media` | Media | media_assets |
| `notifications` | Notification | notification_preferences, notification_logs |

---

## 2. Entity-Relationship (Kern-Entitäten)

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   tenants   │───1:N─│    users    │───1:N─│  sessions   │
└──────┬──────┘       └──────┬──────┘       └─────────────┘
       │                     │
       │ 1:N                 │ 1:N
       ▼                     ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ ebay_accounts│      │  listings   │───N:M─│ media_assets│
└──────┬──────┘       └──────┬──────┘       └─────────────┘
       │                     │
       │ 1:N                 │ 1:N
       ▼                     ▼
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ebay_sync_logs│      │  ai_jobs    │       │subscriptions │
└─────────────┘       └─────────────┘       └─────────────┘
```

---

## 3. Tabellen-Definitionen

### 3.1 Identity Schema

**tenants**
| Spalte | Typ | Constraints |
|--------|-----|-------------|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(100) | UNIQUE, NOT NULL |
| plan | VARCHAR(50) | NOT NULL (free, pro, enterprise) |
| settings | JSONB | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | |

**users**
| Spalte | Typ | Constraints |
|--------|-----|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants |
| email | VARCHAR(255) | NOT NULL |
| password_hash | VARCHAR(255) | |
| first_name | VARCHAR(100) | |
| last_name | VARCHAR(100) | |
| role | VARCHAR(50) | DEFAULT 'member' |
| email_verified_at | TIMESTAMPTZ | |
| last_login_at | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | |
| UNIQUE(tenant_id, email) | | |

**sessions**
| Spalte | Typ | Constraints |
|--------|-----|-------------|
| id | UUID | PK |
| user_id | UUID | FK → users |
| token_hash | VARCHAR(255) | UNIQUE |
| expires_at | TIMESTAMPTZ | NOT NULL |
| ip_address | INET | |
| user_agent | TEXT | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |

---

### 3.2 Listings Schema

**listings**
| Spalte | Typ | Constraints |
|--------|-----|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants |
| user_id | UUID | FK → users |
| template_id | UUID | FK → listing_templates (nullable) |
| status | VARCHAR(50) | draft, pending_review, publishing, active, sold, ended, failed |
| vehicle | JSONB | NOT NULL (make, model, year, ...) |
| title | VARCHAR(80) | |
| description | TEXT | |
| price | JSONB | {amount, currency} |
| media_ids | UUID[] | |
| category_id | VARCHAR(50) | eBay Kategorie |
| ebay_item_id | VARCHAR(50) | Nach Sync |
| ebay_url | TEXT | |
| publish_requested_at | TIMESTAMPTZ | |
| published_at | TIMESTAMPTZ | |
| metadata | JSONB | |
| created_at | TIMESTAMPTZ | DEFAULT NOW() |
| updated_at | TIMESTAMPTZ | |
| INDEX(status, tenant_id) | | |
| INDEX(ebay_item_id) | | |

**listing_templates**
| Spalte | Typ | Constraints |
|--------|-----|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants |
| name | VARCHAR(255) | |
| vehicle_defaults | JSONB | |
| description_template | TEXT | |
| category_id | VARCHAR(50) | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

---

### 3.3 eBay Schema

**ebay_accounts**
| Spalte | Typ | Constraints |
|--------|-----|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants |
| user_id | UUID | FK → users |
| ebay_user_id | VARCHAR(100) | |
| access_token_enc | TEXT | Verschlüsselt |
| refresh_token_enc | TEXT | Verschlüsselt |
| token_expires_at | TIMESTAMPTZ | |
| display_name | VARCHAR(255) | |
| is_default | BOOLEAN | DEFAULT false |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

**ebay_sync_logs**
| Spalte | Typ | Constraints |
|--------|-----|-------------|
| id | UUID | PK |
| listing_id | UUID | FK → listings |
| ebay_account_id | UUID | FK → ebay_accounts |
| action | VARCHAR(50) | create, update, end |
| status | VARCHAR(50) | pending, success, failed |
| ebay_item_id | VARCHAR(50) | |
| request_payload | JSONB | |
| response_payload | JSONB | |
| error_message | TEXT | |
| created_at | TIMESTAMPTZ | |
| INDEX(listing_id, created_at) | | |

---

### 3.4 AI Schema

**ai_jobs**
| Spalte | Typ | Constraints |
|--------|-----|-------------|
| id | UUID | PK |
| listing_id | UUID | FK → listings |
| job_type | VARCHAR(50) | description, title, keywords |
| status | VARCHAR(50) | pending, processing, completed, failed |
| input_data | JSONB | |
| output_data | JSONB | |
| model_used | VARCHAR(100) | |
| tokens_used | INTEGER | |
| created_at | TIMESTAMPTZ | |
| completed_at | TIMESTAMPTZ | |
| INDEX(listing_id, status) | | |

---

### 3.5 Billing Schema

**subscriptions**
| Spalte | Typ | Constraints |
|--------|-----|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants |
| plan | VARCHAR(50) | |
| stripe_subscription_id | VARCHAR(255) | |
| stripe_customer_id | VARCHAR(255) | |
| status | VARCHAR(50) | active, cancelled, past_due |
| current_period_start | TIMESTAMPTZ | |
| current_period_end | TIMESTAMPTZ | |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

**usage_records**
| Spalte | Typ | Constraints |
|--------|-----|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants |
| period_start | DATE | |
| period_end | DATE | |
| listings_created | INTEGER | DEFAULT 0 |
| listings_published | INTEGER | DEFAULT 0 |
| ai_tokens_used | INTEGER | DEFAULT 0 |
| api_calls | INTEGER | DEFAULT 0 |
| created_at | TIMESTAMPTZ | |
| UNIQUE(tenant_id, period_start) | | |

---

### 3.6 Media Schema

**media_assets**
| Spalte | Typ | Constraints |
|--------|-----|-------------|
| id | UUID | PK |
| tenant_id | UUID | FK → tenants |
| user_id | UUID | FK → users |
| storage_key | VARCHAR(500) | S3 Key |
| file_name | VARCHAR(255) | |
| content_type | VARCHAR(100) | |
| size_bytes | BIGINT | |
| width | INTEGER | |
| height | INTEGER | |
| checksum | VARCHAR(64) | |
| created_at | TIMESTAMPTZ | |

---

## 4. Row-Level Security (Multi-Tenancy)

```sql
-- Beispiel für listings
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON listings
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

**Hinweis:** `app.tenant_id` wird pro Request vom Application-Layer gesetzt (aus JWT).

---

## 5. Indizes (Performance)

| Tabelle | Index | Zweck |
|---------|-------|-------|
| listings | (tenant_id, status, created_at DESC) | Dashboard-Liste |
| listings | (user_id, created_at DESC) | User-Liste |
| ebay_sync_logs | (listing_id, created_at DESC) | Sync-Historie |
| ai_jobs | (listing_id, status) | Job-Status |
| usage_records | (tenant_id, period_start) | Billing-Aggregation |
| sessions | (token_hash) | Auth-Lookup |
| users | (tenant_id, email) | Login |

---

## 6. Migrations-Strategie

- **Tool:** Flyway oder Liquibase
- **Ordnung:** Pro Service eigene Migration-Dateien im Format `V{version}__{description}.sql`
- **Rollback:** Down-Migrationen für kritische Änderungen definieren
