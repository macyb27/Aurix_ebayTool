# AURIX Backend

eBay Listings Automation Tool – AI-gestütztes Backend.

## Architektur

- **FastAPI** mit async Support
- **SQLAlchemy** + PostgreSQL (async)
- **Celery** + Redis für Background Tasks
- **Services**: EbayService, VisionService, MarketService, PricingService, ListingService

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# .env mit Credentials füllen (eBay, OpenAI, DB)
```

## Start

```bash
# API Server
uvicorn app.main:app --reload

# Celery Worker (separates Terminal)
celery -A app.celery_app worker -l info
```

## API

- Docs: http://localhost:8000/docs
- Health: GET /health
- Endpoints: /api/v1/products, /api/v1/listings, /api/v1/pricing, /api/v1/market, /api/v1/vision

## Tests

```bash
pytest tests/ -v
```
