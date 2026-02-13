#!/usr/bin/env python3
"""
Beispiel: AURIX Agent für eBay Listing-Analyse
"""

import json
import os
import tempfile
from pathlib import Path

from aurix_agent.orchestrator import ListingOrchestrator


def main():
    # Minimales JPEG für Demo (ohne echte Bilder nutzt Vision Fallback)
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(b"\xff\xd8\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' \",#\x1c\x1c(7),01444\x1f\'9=82<.\xff\xd9")
        image_path = f.name
    try:
        orch = ListingOrchestrator(
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            use_ebay_sandbox=True,
        )
        result = orch.analyze(
            image_paths=[image_path],
            market_query="iPhone 12 Pro",
        )
        print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
    finally:
        Path(image_path).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
