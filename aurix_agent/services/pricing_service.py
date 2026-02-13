"""
PricingService - Preisstrategie und Berechnung
Entscheidet Auction vs Fixed und berechnet Startpreis, Fixed Price, erwarteten Gewinn.
"""

import logging
from typing import Literal

from aurix_agent.models import MarketResult, PricingResult, VisionResult

logger = logging.getLogger(__name__)


class PricingService:
    """Berechnet optimale Preisstrategie basierend auf Markt- und Vision-Daten."""

    AUCTION_DEMAND_THRESHOLD = 50
    AUCTION_CONDITION_BOOST = 1.05
    FIXED_DISCOUNT = 0.92

    def analyze(
        self,
        market: MarketResult,
        vision: VisionResult,
    ) -> PricingResult:
        """
        Entscheidet Auction vs Fixed und berechnet Preise.

        Args:
            market: Marktstatistiken
            vision: Produktinformationen aus Bildanalyse

        Returns:
            PricingResult mit strategy, start_price, fixed_price, expected_price
        """
        warnings = []
        median = market.median_price
        q1, q3 = market.q1, market.q3
        demand = market.demand_score
        condition = (vision.condition or "").lower()

        if median <= 0:
            return PricingResult(
                strategy="fixed",
                start_price=0.0,
                fixed_price=0.0,
                expected_price=0.0,
                reasoning="Keine Marktdaten verfügbar.",
                warnings=["Keine Marktpreise für Preisberechnung."],
            )

        # Strategie: Auction bei hohem Demand, sonst Fixed
        use_auction = demand >= self.AUCTION_DEMAND_THRESHOLD
        if "neu" in condition or "refurbished" in condition:
            use_auction = demand >= 40

        if use_auction:
            start_price = q1 * 0.85
            expected_price = median * self.AUCTION_CONDITION_BOOST
            if "neu" in condition:
                expected_price *= 1.1
            strategy: Literal["auction", "fixed"] = "auction"
            reasoning = (
                f"Demand Score {demand} >= {self.AUCTION_DEMAND_THRESHOLD}. "
                "Auktion empfohlen für potenziell höheren Erlös."
            )
        else:
            start_price = 0.0
            fixed_price = median * self.FIXED_DISCOUNT
            expected_price = fixed_price
            strategy = "fixed"
            reasoning = (
                f"Demand Score {demand} < {self.AUCTION_DEMAND_THRESHOLD}. "
                "Festpreis für schnelleren, vorhersehbaren Verkauf."
            )

        if vision.confidence < 0.6:
            warnings.append(
                "Niedrige Vision-Confidence. Preise manuell prüfen."
            )
        if market.sample_count < 10:
            warnings.append(
                f"Nur {market.sample_count} Vergleichsverkäufe. "
                "Statistik unsicher."
            )

        final_start = round(start_price, 2) if strategy == "auction" else 0.0
        final_fixed = round(max(0.01, median * self.FIXED_DISCOUNT), 2) if strategy == "fixed" else 0.0
        return PricingResult(
            strategy=strategy,
            start_price=final_start,
            fixed_price=final_fixed,
            expected_price=round(max(0.01, expected_price), 2),
            reasoning=reasoning,
            warnings=warnings,
        )
