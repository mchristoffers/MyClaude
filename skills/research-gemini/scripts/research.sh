#!/usr/bin/env bash
# Run Gemini CLI headlessly as a web-research agent. Usage: research.sh "<question>"
set -euo pipefail

question="${1:?usage: research.sh <question>}"
model_flag=()
if [ -n "${GEMINI_RESEARCH_MODEL:-}" ]; then
  model_flag=(-m "$GEMINI_RESEARCH_MODEL")
fi

gemini -p "$question" --approval-mode yolo --skip-trust "${model_flag[@]}"
