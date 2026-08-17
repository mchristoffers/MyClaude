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

# Gemini CLI reads the same ~/.agents/skills tree, so it can discover this very
# skill and shell back out to this script — an infinite delegation loop that
# just hangs. The skill is disabled for Gemini at user scope
# (`gemini skills disable research-gemini --scope user`); this guard catches the
# case where that setting is gone, and tells the child what to do instead.
if [ -n "${GEMINI_RESEARCH_ACTIVE:-}" ]; then
  echo "You are already the research agent — do not call research.sh." >&2
  echo "Use your own google_web_search tool and answer directly." >&2
  exit 1
fi
export GEMINI_RESEARCH_ACTIVE=1

model_flag=()
if [ -n "${GEMINI_RESEARCH_MODEL:-}" ]; then
  model_flag=(-m "$GEMINI_RESEARCH_MODEL")
fi

gemini -p "$question" --approval-mode yolo --skip-trust "${model_flag[@]}"
