#!/usr/bin/env python3
"""Extract coverage score from coverage.json"""

import json
import sys
import os

filepath = sys.argv[1] if len(sys.argv) > 1 else "coverage.json"

try:
    with open(filepath, 'r') as f:
        data = json.load(f)
        coverage = data.get("totals", {}).get("percent_covered", 0.0)
        print(f"{coverage:.1f}")
except Exception:
    print("0.0")
    sys.exit(0)
