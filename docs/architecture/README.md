# eBay Auto-Listing Tool – Architektur

Dieses Verzeichnis enthält die vollständige Systemarchitektur-Spezifikation. **Kein funktionierender Feature-Code**, nur Architektur-Definitionen.

## Dokumenten-Index

```
00-ARCHITECTURE-OVERVIEW.md   → Einstieg, High-Level, Tech-Stack
01-SERVICE-BOUNDARIES.md     → Service-Grenzen, Abhängigkeiten
02-API-CONTRACTS.md          → REST + Event-Interfaces
03-DATABASE-SCHEMA.md        → DB-Schema pro Service
04-EVENT-FLOWS.md            → Event-Sequenzen, Retry, Idempotenz
05-SECURITY-SCALABILITY.md   → NFRs, SaaS, Checklisten
06-AGENT-REVIEW-CHECKLIST.md → Prüfung von Agent-Vorschlägen
```

## Lesereihenfolge

1. **Überblick**: 00-ARCHITECTURE-OVERVIEW.md
2. **Services**: 01-SERVICE-BOUNDARIES.md
3. **Schnittstellen**: 02-API-CONTRACTS.md
4. **Daten**: 03-DATABASE-SCHEMA.md
5. **Flows**: 04-EVENT-FLOWS.md
6. **NFRs**: 05-SECURITY-SCALABILITY.md

## Architektur-Prinzipien

- **Modular**: Service pro Bounded Context
- **Event-Driven**: Async-Kommunikation über Message Queue
- **SaaS-Ready**: Multi-Tenancy, Subscriptions, Usage-Tracking
- **Erweiterbar**: Klare Contracts, keine versteckten Abhängigkeiten

## Verwendung

- **Architect Agent**: Nutzt diese Spezifikation als Referenz
- **Feature Agents**: Müssen die Architektur einhalten
- **Review**: 06-AGENT-REVIEW-CHECKLIST.md bei jedem Vorschlag prüfen
