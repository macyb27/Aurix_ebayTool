# eBay Auto-Listing Tool – Systemarchitektur

## 1. Architektur-Übersicht

### 1.1 Vision
Ein SaaS-fähiges, AI-gestütztes eBay-Listing-Automatisierungstool für Händler mit Multi-Tenancy, skalierbarer Event-Architektur und klarer Service-Trennung.

### 1.2 Architekturprinzipien
| Prinzip | Beschreibung |
|---------|--------------|
| **Modularität** | Jeder Service hat eine einzige Verantwortung (SRP) |
| **Lose Kopplung** | Kommunikation über Events und definierte APIs |
| **Hohe Kohäsion** | Domänenlogik bleibt innerhalb der Service-Grenzen |
| **SaaS-Ready** | Multi-Tenancy, Subscription-Management, Usage-Tracking |
| **API-First** | Alle Schnittstellen als OpenAPI/JSON spezifiziert |

### 1.3 High-Level Systemkontext

```mermaid
C4Context
    title System Context - eBay Auto-Listing Tool
    Person(haendler, "eBay-Händler", "Erstellt und verwaltet Listings")
    Person(admin, "Tenant-Admin", "Verwaltet Organisation und Nutzer")
    
    System(ebay_tool, "eBay Auto-Listing Tool", "AI-gestützte Listing-Automatisierung")
    System_Ext(ebay_api, "eBay API", "Offizielle eBay Handels-API")
    System_Ext(ai_provider, "AI Provider", "LLM für Beschreibungen, Bildanalyse")
    
    Rel(haendler, ebay_tool, "Nutzt")
    Rel(admin, ebay_tool, "Verwaltet")
    Rel(ebay_tool, ebay_api, "Listings erstellen/aktualisieren")
    Rel(ebay_tool, ai_provider, "AI-Features")
```

### 1.4 Technologie-Stack (Empfehlung)

| Schicht | Technologie | Begründung |
|---------|-------------|------------|
| **Frontend** | React/Next.js oder Vue/Nuxt | SPA/SSR, TypeScript, Komponenten |
| **API Gateway** | Kong / AWS API Gateway | Rate-Limiting, Auth, Routing |
| **Backend Services** | Node.js (NestJS) oder Python (FastAPI) | Async, Ökosystem |
| **Message Broker** | RabbitMQ / AWS SQS | Event-Driven, Zuverlässigkeit |
| **Datenbank** | PostgreSQL | ACID, JSONB, Skalierbarkeit |
| **Cache** | Redis | Sessions, Rate-Limits, Caching |
| **Object Storage** | S3/MinIO | Bilder, Dokumente |
| **AI Integration** | OpenAI/Anthropic API | LLM für Beschreibungen |

---

## 2. Service-Landschaft

### 2.1 Bounded Contexts

```mermaid
graph TB
    subgraph "Frontend Layer"
        WEB[Web Application]
    end
    
    subgraph "API Layer"
        GW[API Gateway]
    end
    
    subgraph "Core Services"
        AUTH[Auth Service]
        TENANT[Tenant Service]
        LISTING[Listing Service]
        INVENTORY[Inventory Service]
        AI[AI Service]
        SYNC[Sync Service]
    end
    
    subgraph "Integration Services"
        EBAY[eBay Adapter]
    end
    
    subgraph "Shared"
        EVENTS[Event Bus]
        DB[(PostgreSQL)]
        CACHE[(Redis)]
    end
    
    WEB --> GW
    GW --> AUTH
    GW --> TENANT
    GW --> LISTING
    GW --> INVENTORY
    GW --> AI
    
    LISTING --> EVENTS
    INVENTORY --> EVENTS
    AI --> EVENTS
    SYNC --> EVENTS
    SYNC --> EBAY
    EBAY --> EVENTS
    
    AUTH --> DB
    TENANT --> DB
    LISTING --> DB
    INVENTORY --> DB
    SYNC --> DB
    AUTH --> CACHE
```

### 2.2 Service-Matrix

| Service | Verantwortung | Datenbesitz | Events (Out) | Events (In) |
|---------|---------------|-------------|--------------|-------------|
| **Auth Service** | Authentifizierung, Autorisierung, Sessions | Users, Sessions, Permissions | UserCreated, SessionRevoked | - |
| **Tenant Service** | Multi-Tenancy, Organisationen, Subscriptions | Tenants, Plans, Billing | TenantCreated, PlanChanged | - |
| **Listing Service** | Listing-Erstellung, -Bearbeitung, -Workflows | Listings, Templates | ListingCreated, ListingPublished | InventorySynced |
| **Inventory Service** | Produktdaten, Varianten, Bestände | Products, Variants, Stock | InventorySynced, StockUpdated | - |
| **AI Service** | Beschreibungen, Bildanalyse, Kategorisierung | AI-Jobs, Prompts | AIJobCompleted | ListingDraftCreated |
| **Sync Service** | eBay-API-Integration, Bidirektionale Synchronisation | Sync-State, eBay-Mappings | ListingPublished, SyncCompleted | ListingApproved |
| **eBay Adapter** | eBay API-Aufrufe, OAuth, Retry-Logik | - (stateless) | - | - |

---

## 3. Deployment-Architektur

```mermaid
graph TB
    subgraph "CDN / Edge"
        CDN[CloudFlare / CloudFront]
    end
    
    subgraph "Load Balancer"
        LB[Load Balancer]
    end
    
    subgraph "Kubernetes Cluster"
        subgraph "Ingress"
            ING[Ingress Controller]
        end
        
        subgraph "API Tier"
            GW1[Gateway Pod 1]
            GW2[Gateway Pod 2]
        end
        
        subgraph "Service Tier"
            SVC1[Service Pods]
            SVC2[Service Pods]
        end
        
        subgraph "Worker Tier"
            W1[Worker Pod 1]
            W2[Worker Pod 2]
        end
    end
    
    subgraph "Data Tier"
        PG[(PostgreSQL Primary)]
        PG_REPLICA[(PostgreSQL Replica)]
        REDIS[(Redis Cluster)]
        MQ[Message Queue]
    end
    
    CDN --> LB
    LB --> ING
    ING --> GW1
    ING --> GW2
    GW1 --> SVC1
    GW2 --> SVC2
    SVC1 --> PG
    SVC2 --> PG_REPLICA
    SVC1 --> REDIS
    SVC1 --> MQ
    MQ --> W1
    MQ --> W2
    W1 --> PG
    W2 --> EBAY_EXT[eBay API]
```

---

## 4. Nächste Dokumente

- [01-SERVICE-BOUNDARIES.md](./01-SERVICE-BOUNDARIES.md) – Detaillierte Service-Grenzen
- [02-API-CONTRACTS.md](./02-API-CONTRACTS.md) – REST/Event-Interfaces
- [03-DATABASE-SCHEMA.md](./03-DATABASE-SCHEMA.md) – Datenmodell
- [04-EVENT-FLOWS.md](./04-EVENT-FLOWS.md) – Event-Sequenzen
- [05-SECURITY-SCALABILITY.md](./05-SECURITY-SCALABILITY.md) – NFRs
