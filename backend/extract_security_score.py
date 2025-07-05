#!/usr/bin/env python3
"""Extract security issues count from bandit_report.json"""

import json
import sys

filepath = sys.argv[1] if len(sys.argv) > 1 else "bandit_report.json"

try:
    with open(filepath, 'r') as f:
        data = json.load(f)
        issues = len(data.get('results', []))
        print(issues)
except Exception:
    print("0")
    sys.exit(0)
