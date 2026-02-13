# eBay Auto-Listing Tool (Aurix) - Architektur-Index

## Übersicht

Dieses Verzeichnis enthält die vollständige Systemarchitektur-Spezifikation für das eBay Auto-Listing Tool. **Kein funktionierender Feature-Code**, nur Architektur-Dokumentation.

## Dokumente

| # | Dokument | Inhalt |
|---|----------|--------|
| 01 | [System-Architektur](./01-SYSTEM-ARCHITECTURE.md) | High-Level Architektur, Tech-Stack, Multi-Tenancy, Deployment |
| 02 | [Service-Grenzen](./02-SERVICE-BOUNDARIES.md) | Service-Verantwortlichkeiten, Abhängigkeiten, Erweiterbarkeit |
| 03 | [API-Contracts](./03-API-CONTRACTS.md) | REST API, Event-Contracts, Webhooks, Fehlercodes |
| 04 | [Datenbankschema](./04-DATABASE-SCHEMA.md) | Tabellen, Indizes, RLS, Migrations |
| 05 | [Event-Flows](./05-EVENT-FLOWS.md) | Prozessabläufe, Sequenzdiagramme, Retry/DLQ |
| 06 | [Sicherheit & Skalierung](./06-SECURITY-SCALABILITY.md) | Zero-Trust, RBAC, Skalierungsstrategien, Agent-Review |

## JSON-Contracts

| Datei | Inhalt |
|-------|--------|
| [api-contracts.json](./contracts/api-contracts.json) | JSON Schema für API-Request/Response |
| [event-contracts.json](./contracts/event-contracts.json) | JSON Schema für Event-Payloads |

## Architektur-Prinzipien

- **Modular:** Klare Service-Grenzen, Event-getrieben
- **Erweiterbar:** Plugin-fähige eBay-Integration, weitere Marketplaces möglich
- **SaaS-fähig:** Multi-Tenancy, Subscription-Management
- **Sicher:** Zero-Trust, Verschlüsselung, RBAC
- **Skalierbar:** Horizontale Skalierung, Caching, Read-Replicas

## Verwendung durch andere Agents

Andere Agents (z.B. Backend, Frontend, DevOps) sollen:

1. **Service-Grenzen** aus `02-SERVICE-BOUNDARIES.md` einhalten
2. **API-Contracts** aus `03-API-CONTRACTS.md` und `contracts/` verwenden
3. **Events** gemäß `event-contracts.json` publizieren/konsumieren
4. **Datenbankschema** aus `04-DATABASE-SCHEMA.md` befolgen
5. **Sicherheits-Checkliste** aus `06-SECURITY-SCALABILITY.md` abarbeiten

## Architect Agent – Review-Kriterien

Vorschläge werden geprüft auf:

- **Konsistenz** mit bestehender Architektur
- **Sicherheit** (Credentials, Input-Validierung, RBAC)
- **Skalierbarkeit** (keine Blocking-Calls, Caching)
- **Modularität** (keine unnötigen Abhängigkeiten)
- **SaaS-Fähigkeit** (Tenant-Isolation, Usage-Tracking)
