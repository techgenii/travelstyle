#!/usr/bin/env python3
"""Extract coverage score from coverage.json"""
import json
import sys

try:
    with open('coverage.json', 'r') as f:
        data = json.load(f)
        coverage = data["totals"]["percent_covered"]
        print(f'{coverage:.1f}')
except Exception as e:
    print('0.0')
    sys.exit(0)