#!/bin/bash

# Generate summary script for CI/CD
# Usage: ./generate_summary.sh <job_name> <summary_script> <summary_file> <summary_format>

JOB_NAME=$1
SUMMARY_SCRIPT=$2
SUMMARY_FILE=$3
SUMMARY_FORMAT=$4

# Debug information
echo "Job: $JOB_NAME"
echo "Script: $SUMMARY_SCRIPT"
echo "File: $SUMMARY_FILE"
echo "Format: $SUMMARY_FORMAT"

# Determine the correct report file path based on job name
case "$JOB_NAME" in
    "test"|"coverage")
        REPORT_FILE="reports/coverage.json"
        ;;
    "security")
        REPORT_FILE="reports/bandit_report.json"
        ;;
    "lint")
        REPORT_FILE="reports/pylint_score.txt"
        ;;
    *)
        REPORT_FILE="reports/${JOB_NAME}_report.json"
        ;;
esac

echo "Looking for report file: $REPORT_FILE"

if [ -f "$REPORT_FILE" ]; then
    echo "Found report file: $REPORT_FILE"
    SCORE=$(python ${SUMMARY_SCRIPT} "$REPORT_FILE")
    echo "Extracted score: '$SCORE'"
    
    # Handle empty or invalid score
    if [ -z "$SCORE" ] || [ "$SCORE" = "None" ] || [ "$SCORE" = "null" ]; then
        SCORE="0"
    fi
    
    SUMMARY="${SUMMARY_FORMAT}"
    SUMMARY="${SUMMARY//{score}/$SCORE}"
    echo "Final summary: $SUMMARY"
    echo "$SUMMARY" > ${SUMMARY_FILE}
else
    echo "No report file found: $REPORT_FILE"
    SUMMARY="${SUMMARY_FORMAT}"
    SUMMARY="${SUMMARY//{score}/0 (no report generated)}"
    echo "No report summary: $SUMMARY"
    SUMMARY="${SUMMARY_FORMAT}"
    SUMMARY="${SUMMARY//{score}/0}"
    echo "$SUMMARY" > ${SUMMARY_FILE}
fi 