"""
ListingService - SEO-optimierte Listing-Generierung
Erstellt Titel, Untertitel, HTML-Beschreibung und Item Specifics.
"""

import html
import logging
import re
from typing import Any

from aurix_agent.models import ListingResult, MarketResult, PricingResult, VisionResult

logger = logging.getLogger(__name__)

MAX_TITLE_LENGTH = 80
MAX_SUBTITLE_LENGTH = 55


class ListingService:
    """Generiert SEO-optimierte eBay-Listing-Inhalte."""

    def generate(
        self,
        vision: VisionResult,
        market: MarketResult,
        pricing: PricingResult,
    ) -> ListingResult:
        """
        Erstellt vollständiges Listing-Material.

        Args:
            vision: Produktinformationen
            market: Marktstatistiken
            pricing: Preisstrategie

        Returns:
            ListingResult mit title, subtitle, description_html, item_specifics
        """
        warnings = []
        product = vision.product_name or "Produkt"
        brand = vision.brand or "Unbekannt"
        model = vision.model or ""
        category = vision.category or ""
        condition = vision.condition or "Gebraucht - Gut"

        # SEO-Titel: Brand + Model + Produkt + relevante Keywords
        title = self._build_title(product, brand, model, condition)
        if len(title) > MAX_TITLE_LENGTH:
            title = title[: MAX_TITLE_LENGTH - 3] + "..."
            warnings.append(f"Titel auf {MAX_TITLE_LENGTH} Zeichen gekürzt.")
        title = title.strip()

        # Untertitel: Zusatzinfo, Preis-Hinweis
        subtitle = self._build_subtitle(pricing, condition)
        if len(subtitle) > MAX_SUBTITLE_LENGTH:
            subtitle = subtitle[: MAX_SUBTITLE_LENGTH - 3] + "..."
        subtitle = subtitle.strip()

        # HTML-Beschreibung
        description_html = self._build_description(
            product=product,
            brand=brand,
            model=model,
            condition=condition,
            category=category,
            pricing=pricing,
        )

        # Item Specifics (eBay-Standardfelder)
        item_specifics = self._build_item_specifics(
            brand=brand,
            model=model,
            condition=condition,
            category=category,
        )

        keywords = self._extract_keywords(product, brand, model, category)

        if vision.confidence < 0.6:
            warnings.append("Listing basiert auf unsicherer Bildanalyse. Prüfen.")

        return ListingResult(
            title=title,
            subtitle=subtitle,
            description_html=description_html,
            item_specifics=item_specifics,
            keywords=keywords,
            warnings=warnings,
        )

    def _build_title(self, product: str, brand: str, model: str, condition: str) -> str:
        parts = []
        if brand and brand != "Unbekannt":
            parts.append(brand)
        if model:
            parts.append(model)
        parts.append(product)
        if condition:
            cond_short = condition.replace("Gebraucht - ", "").replace("Refurbished", "Generalüberholt")
            parts.append(f"({cond_short})")
        return " ".join(p for p in parts if p)

    def _build_subtitle(self, pricing: PricingResult, condition: str) -> str:
        if pricing.strategy == "auction":
            return f"Startpreis €{pricing.start_price:.2f} | {condition}"
        return f"Festpreis €{pricing.fixed_price:.2f} | {condition}"

    def _build_description(
        self,
        product: str,
        brand: str,
        model: str,
        condition: str,
        category: str,
        pricing: PricingResult,
    ) -> str:
        esc = html.escape
        sections = [
            f"<h2>{esc(product)}</h2>",
            "<p><strong>Produktdetails:</strong></p>",
            "<ul>",
            f"<li>Marke: {esc(brand)}</li>",
            f"<li>Modell: {esc(model or 'N/A')}</li>",
            f"<li>Zustand: {esc(condition)}</li>",
            f"<li>Kategorie: {esc(category or 'N/A')}</li>",
            "</ul>",
            f"<p>{esc(condition)}. Bitte Bilder beachten - sie sind Bestandteil der Beschreibung.</p>",
            "<p>Bei Fragen gerne melden. Viel Erfolg beim Bieten!</p>",
        ]
        return "\n".join(sections)

    def _build_item_specifics(
        self,
        brand: str,
        model: str,
        condition: str,
        category: str,
    ) -> dict[str, str]:
        specifics: dict[str, str] = {}
        if brand and brand != "Unbekannt":
            specifics["Marke"] = brand
        if model:
            specifics["Modell"] = model
        if condition:
            specifics["Zustand"] = condition
        if category:
            specifics["Kategorie"] = category
        return specifics

    def _extract_keywords(
        self,
        product: str,
        brand: str,
        model: str,
        category: str,
    ) -> list[str]:
        words = re.findall(r"\w+", f"{product} {brand} {model} {category}".lower())
        return list(dict.fromkeys(w for w in words if len(w) > 2))[:15]
