# Aurix_ebayTool

eBay listings automation tool – AI-gestützt, SaaS-fähig, modular.

## Architektur-Dokumentation

Die vollständige Systemarchitektur ist unter `docs/architecture/` dokumentiert:

| Dokument | Inhalt |
|----------|--------|
| [00-ARCHITECTURE-OVERVIEW.md](docs/architecture/00-ARCHITECTURE-OVERVIEW.md) | Systemkontext, Service-Landschaft, Tech-Stack |
| [01-SERVICE-BOUNDARIES.md](docs/architecture/01-SERVICE-BOUNDARIES.md) | Service-Grenzen, Abhängigkeiten, Bounded Contexts |
| [02-API-CONTRACTS.md](docs/architecture/02-API-CONTRACTS.md) | REST-APIs, Event-Contracts, Fehlerformat |
| [03-DATABASE-SCHEMA.md](docs/architecture/03-DATABASE-SCHEMA.md) | Datenmodell pro Service, ER-Diagramme |
| [04-EVENT-FLOWS.md](docs/architecture/04-EVENT-FLOWS.md) | Event-Sequenzen, Retry, Idempotenz |
| [05-SECURITY-SCALABILITY.md](docs/architecture/05-SECURITY-SCALABILITY.md) | Sicherheit, Skalierbarkeit, SaaS-Aspekte |
| [06-AGENT-REVIEW-CHECKLIST.md](docs/architecture/06-AGENT-REVIEW-CHECKLIST.md) | Prüfliste für Agent-Vorschläge |

## Contracts

- **OpenAPI**: `contracts/openapi/*.yaml`
- **Event-Schemas**: `contracts/events/*.json`

## Quick Start (geplant)

- Backend: NestJS/FastAPI
- Frontend: React/Next.js
- DB: PostgreSQL
- Queue: RabbitMQ
