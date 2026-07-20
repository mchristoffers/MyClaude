#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: master1-api.sh METHOD /path [json-body-file]

Calls master-1's internal Coolify API through a temporary SSH local forward.
The bearer token is read locally and never printed or placed in the SSH command.

Environment overrides:
  MASTER1_SSH_HOST       SSH alias (default: master-1)
  MASTER1_TOKEN_FILE     token path (default: ~/.bbj_coolify_token)
  MASTER1_SSH_TIMEOUT    seconds (default: 10)
EOF
}

if [[ ${1:-} == "-h" || ${1:-} == "--help" ]]; then
  usage
  exit 0
fi

if (( $# < 2 || $# > 3 )); then
  usage >&2
  exit 2
fi

method=${1^^}
api_path=$2
body_file=${3:-}
ssh_host=${MASTER1_SSH_HOST:-master-1}
token_file=${MASTER1_TOKEN_FILE:-${HOME}/.bbj_coolify_token}
ssh_timeout=${MASTER1_SSH_TIMEOUT:-10}

case "$method" in
  GET|POST|PUT|PATCH|DELETE) ;;
  *) echo "Unsupported HTTP method: $method" >&2; exit 2 ;;
esac

[[ $api_path == /* ]] || { echo "API path must begin with /" >&2; exit 2; }
[[ -r $token_file ]] || { echo "Token file is not readable: $token_file" >&2; exit 1; }
if [[ -n $body_file && ! -r $body_file ]]; then
  echo "JSON body file is not readable: $body_file" >&2
  exit 1
fi

token_mode=$(stat -c '%a' "$token_file" 2>/dev/null || stat -f '%Lp' "$token_file")
if [[ $token_mode != 600 && $token_mode != 400 ]]; then
  echo "Refusing token file with unsafe mode $token_mode (expected 600 or 400)" >&2
  exit 1
fi

local_port=$(python3 - <<'PY'
import socket
s = socket.socket()
s.bind(("127.0.0.1", 0))
print(s.getsockname()[1])
s.close()
PY
)

ssh -o BatchMode=yes \
  -o ExitOnForwardFailure=yes \
  -o "ConnectTimeout=${ssh_timeout}" \
  -L "127.0.0.1:${local_port}:127.0.0.1:8000" \
  -N "$ssh_host" &
ssh_pid=$!
cleanup() {
  kill "$ssh_pid" 2>/dev/null || true
  wait "$ssh_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

ready=false
for _ in {1..40}; do
  if ! kill -0 "$ssh_pid" 2>/dev/null; then
    wait "$ssh_pid" || true
    echo "SSH forwarding to $ssh_host failed" >&2
    exit 1
  fi
  if curl -fsS --max-time 1 "http://127.0.0.1:${local_port}/api/v1/health" >/dev/null 2>&1; then
    ready=true
    break
  fi
  sleep 0.1
done
[[ $ready == true ]] || { echo "Coolify API did not become reachable through SSH" >&2; exit 1; }

token=$(<"$token_file")
curl_args=(
  --fail-with-body --silent --show-error
  --request "$method"
  --header "Authorization: Bearer ${token}"
  --header "Accept: application/json"
  "http://127.0.0.1:${local_port}/api/v1${api_path}"
)
if [[ -n $body_file ]]; then
  curl_args+=(--header "Content-Type: application/json" --data-binary "@${body_file}")
fi
curl "${curl_args[@]}"
