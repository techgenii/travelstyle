#!/usr/bin/env python3
"""Extract lint score from pylint_report.json"""

import json
import sys

def extract_lint_score(filepath):
    """Extract lint score from pylint_report.json"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            if isinstance(data, list) and len(data) > 0:
                score = data[0].get('score', 0.0)
            else:
                score = data.get('score', 0.0)
            return f"{score:.1f}"
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        return "0.0"

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "reports/pylint_report.json"
    print(extract_lint_score(filepath))
