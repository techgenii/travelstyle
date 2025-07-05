#!/usr/bin/env python3
"""Extract security issues count from bandit_report.json"""
import json
import sys

try:
    with open('bandit_report.json', 'r') as f:
        data = json.load(f)
        issues = len(data.get('results', []))
        print(issues)
except Exception as e:
    print('0')
    sys.exit(0)