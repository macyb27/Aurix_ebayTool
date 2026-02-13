# eBay Auto-Listing Tool - Systemarchitektur

## 1. Übersicht

Das eBay Auto-Listing Tool (Aurix) ist eine SaaS-fähige Plattform zur KI-gestützten Automatisierung von eBay-Fahrzeuginseraten. Die Architektur folgt dem **Domain-Driven Design** und **Event-Driven Architecture** Prinzipien.

### 1.1 Architekturprinzipien

| Prinzip | Umsetzung |
|---------|-----------|
| **Modularität** | Microservices mit klaren Domain-Grenzen |
| **Erweiterbarkeit** | Plugin-basierte eBay-Integration, Event-Sourcing für Audit |
| **SaaS-Fähigkeit** | Multi-Tenancy, Subscription-Management, Ressourcen-Isolation |
| **Skalierbarkeit** | Horizontale Skalierung, Queue-basierte Verarbeitung |
| **Sicherheit** | Zero-Trust, OAuth2, Verschlüsselung at-rest und in-transit |

---

## 2. High-Level Architektur

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           CLIENT LAYER                                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                            │
│  │ Web App      │  │ Mobile App   │  │ API Clients  │                            │
│  │ (React/Next) │  │ (Optional)   │  │ (3rd Party)  │                            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘                            │
└─────────┼─────────────────┼─────────────────┼───────────────────────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────────────────┐
│                        API GATEWAY                                                │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │ Auth │ Rate Limiting │ Request Routing │ API Versioning │ CORS               │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────────────────┐
│                     APPLICATION LAYER (BFF / Services)                            │
│                                                                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │ User        │ │ Listing     │ │ eBay        │ │ AI/ML       │ │ Billing    │ │
│  │ Service     │ │ Service     │ │ Integration │ │ Service     │ │ Service    │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────┬──────┘ │
│         │               │               │               │              │        │
└─────────┼───────────────┼───────────────┼───────────────┼──────────────┼────────┘
          │               │               │               │              │
┌─────────▼───────────────▼───────────────▼───────────────▼──────────────▼────────┐
│                     MESSAGE BROKER (Event Bus)                                   │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │ RabbitMQ / Apache Kafka - Topics: listings, users, ebay-sync, ai-jobs        │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────────────────┐
│                     DATA LAYER                                                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │ PostgreSQL  │ │ Redis       │ │ S3/Blob     │ │ Vector DB   │ │ eBay API   │ │
│  │ (Primary)   │ │ (Cache)     │ │ (Media)     │ │ (Embeddings)│ │ (External) │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technologie-Stack (Empfehlung)

| Schicht | Technologie | Begründung |
|---------|-------------|------------|
| **Frontend** | Next.js 14+ (App Router), React, Tailwind | SSR, SEO für Listing-Previews |
| **API Gateway** | Kong / AWS API Gateway / Traefik | Rate Limiting, Auth, Routing |
| **Backend** | Node.js (NestJS) / Python (FastAPI) | Async, Ökosystem für eBay SDK |
| **Message Broker** | RabbitMQ (Standard) / Kafka (High-Scale) | Event-Driven, Durable |
| **Primary DB** | PostgreSQL 15+ | JSONB, Full-Text, ACID |
| **Cache** | Redis 7+ | Session, Rate-Limit, Job-Queue |
| **Object Storage** | S3 / MinIO | Fahrzeugbilder, Dokumente |
| **Vector DB** | pgvector / Pinecone | KI-Embeddings für Beschreibungen |
| **AI/ML** | OpenAI API / Azure OpenAI / Local LLM | Beschreibungsgenerierung |
| **Container** | Docker, Kubernetes | Orchestrierung, SaaS-Deployment |
| **Monitoring** | Prometheus, Grafana, OpenTelemetry | Observability |

---

## 4. Multi-Tenancy Modell

| Aspekt | Umsetzung |
|--------|-----------|
| **Tenant-Identifikation** | `tenant_id` in JWT + Header `X-Tenant-ID` |
| **Datenisolation** | Schema-per-tenant ODER Row-Level Security mit `tenant_id` |
| **Ressourcen** | CPU/Memory Limits pro Subscription-Tier |
| **Rate Limits** | Pro Tenant + pro User konfigurierbar |
| **Billing** | Usage-basiert: Listings/Monat, API-Calls, AI-Tokens |

---

## 5. Deployment-Architektur

```
                    ┌─────────────────────────────────────┐
                    │           Load Balancer              │
                    └─────────────────┬───────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         │                            │                            │
         ▼                            ▼                            ▼
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│  API Gateway    │        │  API Gateway     │        │  API Gateway    │
│  (Zone A)       │        │  (Zone B)       │        │  (Zone C)       │
└────────┬────────┘        └────────┬────────┘        └────────┬────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         │                          │                          │
         ▼                          ▼                          ▼
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│  Service Pods   │        │  Service Pods   │        │  Service Pods   │
│  (Auto-Scale)   │        │  (Auto-Scale)   │        │  (Auto-Scale)   │
└─────────────────┘        └─────────────────┘        └─────────────────┘
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │   Managed DB (Primary+Replica) │
                    │   Redis Cluster               │
                    │   Message Broker Cluster      │
                    └───────────────────────────────┘
```

---

## 6. Nächste Dokumente

- [02-SERVICE-BOUNDARIES.md](./02-SERVICE-BOUNDARIES.md) - Detaillierte Service-Grenzen
- [03-API-CONTRACTS.md](./03-API-CONTRACTS.md) - REST/Event API-Spezifikationen
- [04-DATABASE-SCHEMA.md](./04-DATABASE-SCHEMA.md) - Datenbankdesign
- [05-EVENT-FLOWS.md](./05-EVENT-FLOWS.md) - Event- und Prozessflüsse
- [06-SECURITY-SCALABILITY.md](./06-SECURITY-SCALABILITY.md) - Sicherheit & Skalierung
