"""
CLI-Einstiegspunkt für den AURIX Agent
"""

import argparse
import json
import os
import sys
from pathlib import Path

from aurix_agent.orchestrator import ListingOrchestrator


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AURIX Pro eBay Auto-Listing Tool - AI/ML Agent"
    )
    parser.add_argument(
        "images",
        nargs="+",
        type=Path,
        help="1-3 Produktbilder (Pfade)",
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        default=None,
        help="Suchbegriff für Marktanalyse (sonst aus Vision)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="JSON in Datei schreiben",
    )
    parser.add_argument(
        "--no-sandbox",
        action="store_true",
        help="eBay Production API statt Sandbox",
    )
    args = parser.parse_args()

    if len(args.images) > 3:
        print("Fehler: Maximal 3 Bilder erlaubt.", file=sys.stderr)
        return 1

    missing = [p for p in args.images if not p.exists()]
    if missing:
        print(f"Fehler: Bilder nicht gefunden: {missing}", file=sys.stderr)
        return 1

    api_key = os.environ.get("OPENAI_API_KEY")
    orch = ListingOrchestrator(
        openai_api_key=api_key,
        use_ebay_sandbox=not args.no_sandbox,
    )
    result = orch.analyze(
        image_paths=[str(p) for p in args.images],
        openai_api_key=api_key,
        market_query=args.query,
    )
    json_str = result.model_dump_json(indent=2, exclude_none=True)

    if args.output:
        args.output.write_text(json_str, encoding="utf-8")
        print(f"Ergebnis gespeichert: {args.output}")
    else:
        print(json_str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
