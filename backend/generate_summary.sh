#!/bin/bash

# Generate summary script for CI/CD
# Usage: ./generate_summary.sh <job_name> <summary_script> <summary_file> <summary_format>

JOB_NAME=$1
SUMMARY_SCRIPT=$2
SUMMARY_FILE=$3
SUMMARY_FORMAT=$4

if [ -f "reports/${JOB_NAME}_report.json" ]; then
    SCORE=$(python ${SUMMARY_SCRIPT} reports/${JOB_NAME}_report.json)
    SUMMARY="${SUMMARY_FORMAT}"
    SUMMARY="${SUMMARY//{score}/$SCORE}"
    echo "$SUMMARY"
    echo "$SUMMARY" > ${SUMMARY_FILE}
else
    SUMMARY="${SUMMARY_FORMAT}"
    SUMMARY="${SUMMARY//{score}/0 (no report generated)}"
    echo "$SUMMARY"
    SUMMARY="${SUMMARY_FORMAT}"
    SUMMARY="${SUMMARY//{score}/0}"
    echo "$SUMMARY" > ${SUMMARY_FILE}
fi 