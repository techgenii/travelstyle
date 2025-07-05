#!/usr/bin/env python3
"""Extract coverage score from coverage.json"""

import json
import sys

def extract_coverage(filepath):
    """Extract coverage percentage from coverage.json"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            coverage = data.get("totals", {}).get("percent_covered", 0.0)
            return f"{coverage:.1f}"
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        return "0.0"

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "reports/coverage.json"
    print(extract_coverage(filepath))
