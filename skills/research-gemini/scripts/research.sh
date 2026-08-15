#!/usr/bin/env bash
# Run Gemini CLI headlessly as a web-research agent. Usage: research.sh "<question>"
set -euo pipefail

if [ -z "${GEMINI_API_KEY:-}" ] && [ -f "$HOME/.bashrc" ]; then
  # Bash tools often run non-interactive/non-login shells, and ~/.bashrc
  # itself bails out early for non-interactive shells (the "case $- in *i*"
  # guard), so a plain `source` never reaches the export below it. Pull just
  # the GEMINI_API_KEY line out directly instead.
  eval "$(grep -m1 '^export GEMINI_API_KEY=' "$HOME/.bashrc" || true)"
fi

question="${1:?usage: research.sh <question>}"
model_flag=()
if [ -n "${GEMINI_RESEARCH_MODEL:-}" ]; then
  model_flag=(-m "$GEMINI_RESEARCH_MODEL")
fi

gemini -p "$question" --approval-mode yolo --skip-trust "${model_flag[@]}"
