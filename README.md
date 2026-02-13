# AURIX Pro eBay Auto-Listing Tool

AI/ML-gestütztes Tool zur automatischen Erstellung von eBay-Listings.

## Services

| Service | Beschreibung |
|---------|--------------|
| **VisionService** | Analysiert 1–3 Bilder via OpenAI Vision API, liefert Produktname, Marke, Modell, Kategorie, Zustand, Confidence |
| **MarketService** | eBay Browse API oder Sandbox: Median, Q1, Q3, Demand Score (0–100) |
| **PricingService** | Entscheidet Auction vs Fixed, berechnet Startpreis, Festpreis, erwarteten Erlös |
| **ListingService** | SEO-optimierter Titel, Untertitel, HTML-Beschreibung, Item Specifics |

## Installation

```bash
pip install -e .
```

## Konfiguration

| Variable | Beschreibung |
|----------|--------------|
| `OPENAI_API_KEY` | OpenAI API-Key für Vision-Analyse |
| `EBAY_CLIENT_ID` | eBay App Client ID |
| `EBAY_CLIENT_SECRET` | eBay App Client Secret |

Ohne `OPENAI_API_KEY` nutzt der VisionService einen Fallback. Ohne eBay-Credentials nutzt der MarketService simulierte Sandbox-Daten.

## Verwendung

### Python API

```python
from aurix_agent import ListingOrchestrator

orch = ListingOrchestrator(openai_api_key="sk-...", use_ebay_sandbox=True)
result = orch.analyze(image_paths=["bild1.jpg", "bild2.jpg"])
json_str = result.model_dump_json(indent=2)
```

### CLI

```bash
aurix-agent bild1.jpg bild2.jpg --query "iPhone 12" -o output.json
```

### Output-Format

```json
{
  "vision": {
    "product_name": "...",
    "brand": "...",
    "model": "...",
    "category": "...",
    "condition": "...",
    "confidence": 0.0–1.0,
    "warnings": []
  },
  "market": {
    "median_price": 0.0,
    "q1": 0.0,
    "q3": 0.0,
    "demand_score": 0–100,
    "sample_count": 0,
    "warnings": []
  },
  "pricing": {
    "strategy": "auction" | "fixed",
    "start_price": 0.0,
    "fixed_price": 0.0,
    "expected_price": 0.0,
    "reasoning": "...",
    "warnings": []
  },
  "listing": {
    "title": "...",
    "subtitle": "...",
    "description_html": "...",
    "item_specifics": { "key": "value" },
    "keywords": [],
    "warnings": []
  },
  "meta": {
    "overall_confidence": 0.0,
    "warnings": [],
    "hints": []
  }
}
```

## Tests

```bash
pytest tests/ -v
```
