#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: validate-compose.sh REPO_DIR COMPOSE_PATH [ENV_EXAMPLE]" >&2
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi
(( $# >= 2 && $# <= 3 )) || { usage; exit 2; }

repo_dir=$(realpath "$1")
compose_arg=$2
if [[ $compose_arg = /* ]]; then
  compose_file="${repo_dir}${compose_arg}"
else
  compose_file="${repo_dir}/${compose_arg}"
fi
env_file=${3:-${repo_dir}/.env.example}

[[ -d $repo_dir/.git ]] || { echo "ERROR: not a Git repository: $repo_dir" >&2; exit 1; }
[[ -r $compose_file ]] || { echo "ERROR: compose file is not readable: $compose_file" >&2; exit 1; }
command -v docker >/dev/null || { echo "ERROR: docker is required" >&2; exit 1; }
command -v gh >/dev/null || { echo "ERROR: gh is required" >&2; exit 1; }

remote_url=$(git -C "$repo_dir" remote get-url origin)
visibility=$(gh repo view "$remote_url" --json visibility --jq .visibility)
[[ $visibility == PRIVATE ]] || { echo "ERROR: GitHub repository visibility is $visibility, expected PRIVATE" >&2; exit 1; }

if rg -n '^[[:space:]]*build[[:space:]]*:' "$compose_file"; then
  echo "ERROR: custom build entries are outside this upstream-image workflow" >&2
  exit 1
fi
if ! rg -q '^[[:space:]]*image[[:space:]]*:' "$compose_file"; then
  echo "ERROR: no service image entries found" >&2
  exit 1
fi

compose_input=(docker compose -f - config --quiet)
if [[ -r $env_file ]]; then
  compose_input=(docker compose --env-file "$env_file" -f - config --quiet)
else
  echo "WARNING: no env example found; required interpolation variables may prevent validation" >&2
fi

# exclude_from_hc is supported by Coolify but rejected by the stock Compose schema.
sed '/^[[:space:]]*exclude_from_hc[[:space:]]*:/d' "$compose_file" | "${compose_input[@]}"

if rg -n '^[[:space:]]*ports[[:space:]]*:' "$compose_file" >/dev/null; then
  echo "WARNING: host port mappings found; ensure only the intended public service is exposed" >&2
fi
if rg -n '^[[:space:]]*-[[:space:]]*/[^:]+:' "$compose_file" >/dev/null; then
  echo "WARNING: bind mounts found; confirm paths exist on master-1 and are backed up" >&2
fi
if ! rg -q '^volumes:[[:space:]]*$' "$compose_file"; then
  echo "WARNING: no top-level named volumes found; confirm the application is stateless" >&2
fi

echo "OK: private repository and Compose structure validated"
