#!/usr/bin/env python3
"""Extract lint score from pylint_report.json"""

import json
import sys

filepath = sys.argv[1] if len(sys.argv) > 1 else "pylint_report.json"

try:
    with open(filepath, 'r') as f:
        data = json.load(f)
        if isinstance(data, list) and len(data) > 0:
            score = data[0].get('score', 0.0)
        else:
            score = data.get('score', 0.0)
        print(f"{score:.1f}")
except Exception:
    print("0.0")
    sys.exit(0)
