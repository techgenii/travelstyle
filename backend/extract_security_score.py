#!/usr/bin/env python3
"""Extract security issues count from bandit_report.json"""

import json
import sys

def extract_security_issues(filepath):
    """Extract number of security issues from bandit_report.json"""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            issues = len(data.get('results', []))
            return str(issues)
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        return "0"

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "reports/bandit_report.json"
    print(extract_security_issues(filepath))
