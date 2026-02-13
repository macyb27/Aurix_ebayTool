# AURIX eBay Auto-Listing Backend

FastAPI-Backend gemäß Architekturspezifikation.

## Services

| Service | Beschreibung |
|---------|--------------|
| **VisionService** | AI-Bildanalyse, Beschreibungs-Generierung |
| **MarketService** | eBay-Kategorien, Marktdaten |
| **PricingService** | Preisvorschläge, Versandkosten |
| **ListingService** | Listing-Lifecycle, Workflows |
| **EbayService** | eBay-API, Token, Publish, Retry |

## Setup

```bash
# Virtualenv (empfohlen)
python -m venv venv
source venv/bin/activate  # oder Windows: venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Umgebungsvariablen
cp .env.example .env
# .env bearbeiten (DB, Redis, eBay, AI)
```

## Datenbank

```bash
# PostgreSQL starten, DB "aurix" anlegen
# Migration
alembic upgrade head
```

## Server starten

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Celery Worker

```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

## Tests

```bash
pytest tests/ -v
```

## API Endpoints

- `GET/POST /v1/listings` – Listings
- `POST /v1/listings/:id/approve` – Freigabe
- `POST /v1/listings/:id/publish` – Bei eBay veröffentlichen
- `POST /v1/listings/:id/generate-ai` – AI-Generierung (async)
- `GET/POST /v1/ai/*` – Vision/AI
- `GET/POST /v1/market/categories` – Kategorien
- `POST /v1/pricing/suggest` – Preisvorschlag
- `GET /v1/sync/status/:listingId` – Sync-Status

**Header:** `X-Tenant-Id: <uuid>` (erforderlich)
