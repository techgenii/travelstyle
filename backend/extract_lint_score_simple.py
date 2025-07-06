#!/usr/bin/env python3
"""Extract lint score from pylint_score.txt"""

import sys

def extract_lint_score(filepath):
    """Extract lint score from pylint_score.txt"""
    try:
        with open(filepath, 'r') as f:
            score = f.read().strip()
            if score and score != "0.0":
                return f"{float(score):.1f}"
            else:
                return "0.0"
    except (FileNotFoundError, ValueError):
        return "0.0"

if __name__ == "__main__":
    filepath = sys.argv[1] if len(sys.argv) > 1 else "reports/pylint_score.txt"
    print(extract_lint_score(filepath)) 