# Aurix eBay Tool

eBay listings automation tool – AI-powered, SaaS-ready.

## Architektur

Die vollständige Systemarchitektur ist in [`docs/architecture/`](docs/architecture/) dokumentiert:

- **[Architektur-Index](docs/architecture/00-INDEX.md)** – Übersicht aller Spezifikationen
- **System-Architektur** – High-Level Design, Tech-Stack, Multi-Tenancy
- **Service-Grenzen** – Microservices, Abhängigkeiten, Erweiterbarkeit
- **API-Contracts** – REST API, Events, Webhooks
- **Datenbankschema** – Tabellen, Indizes, RLS
- **Event-Flows** – Prozessabläufe, Sequenzdiagramme
- **Sicherheit & Skalierung** – Zero-Trust, RBAC, Skalierungsstrategien

## Tech-Stack (Empfehlung)

- **Frontend:** Next.js, React, Tailwind
- **Backend:** Node.js (NestJS) / Python (FastAPI)
- **DB:** PostgreSQL, Redis
- **Message Broker:** RabbitMQ / Kafka
- **AI:** OpenAI API / Azure OpenAI
- **Deployment:** Docker, Kubernetes
