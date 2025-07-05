#!/usr/bin/env python3
"""Extract lint score from pylint_report.json"""
import json
import sys

try:
    with open('pylint_report.json', 'r') as f:
        data = json.load(f)
        if isinstance(data, list) and len(data) > 0:
            score = data[0].get('score', 0.0) if 'score' in data[0] else 0.0
        else:
            score = data.get('score', 0.0)
        print(f'{score:.1f}')
except Exception as e:
    print('0.0')
    sys.exit(0)