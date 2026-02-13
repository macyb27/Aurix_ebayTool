# AURIX Backend Architekturspezifikation

## Projektstruktur

```
aurix_backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI Application
│   ├── config.py               # Konfiguration
│   ├── database.py             # Async SQLAlchemy Setup
│   ├── models/                 # SQLAlchemy Models
│   ├── schemas/                # Pydantic Schemas
│   ├── services/               # Business Logic Services
│   ├── api/                    # API Router & Endpoints
│   ├── core/                   # Token, Retry, Error Handling
│   └── celery_app.py           # Celery Konfiguration
├── tests/
├── alembic/
└── requirements.txt
```

## Service-Layer Architektur

- **EbayService**: eBay API Kommunikation, OAuth Token Handling, Retry-Logik
- **VisionService**: Bildanalyse (Produkterkennung, Kategorisierung)
- **MarketService**: Marktanalyse, Trend-Daten
- **PricingService**: Preiskalkulation, Wettbewerbsanalyse
- **ListingService**: Listing-Erstellung, -Verwaltung, Orchestrierung

## Datenfluss

1. Frontend → API Endpoints → Services → Database/External APIs
2. Background Tasks: Celery → Services
3. eBay API: Token Refresh, Retry bei 429/5xx
