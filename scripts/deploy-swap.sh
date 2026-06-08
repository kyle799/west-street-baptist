#!/usr/bin/env bash
# Zero-downtime blue-green swap of the Django web service.
#
# Usage (run on the VPS from the repo root):
#   scripts/deploy-swap.sh
#
# Assumes .env already has the new IMAGE_TAG (the CI workflow writes it
# before invoking us). Reads the current color out of
# nginx/upstream/active-upstream.conf, starts the OTHER color with the new image,
# waits for its container healthcheck to pass, rewrites the upstream file,
# reloads nginx, then stops the old color.
#
# If anything fails before the nginx swap, the old color keeps serving
# traffic and the deploy exits non-zero — safe to retry.
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

COMPOSE=(docker compose -f docker-compose.prod.yml)
UPSTREAM_FILE="$REPO_ROOT/nginx/upstream/active-upstream.conf"
UPSTREAM_TEMPLATE="$REPO_ROOT/nginx/upstream/active-upstream.conf.example"
HEALTH_TIMEOUT=120  # seconds (covers migrate + collectstatic on boot)

# Bootstrap the live upstream file on first install.
if [[ ! -f "$UPSTREAM_FILE" ]]; then
  if [[ ! -f "$UPSTREAM_TEMPLATE" ]]; then
    echo "!! $UPSTREAM_FILE missing and $UPSTREAM_TEMPLATE also absent" >&2
    exit 1
  fi
  echo "==> bootstrapping $UPSTREAM_FILE from template"
  cp "$UPSTREAM_TEMPLATE" "$UPSTREAM_FILE"
fi

# Decide current / next color.
running_blue="$("${COMPOSE[@]}" ps -q web-blue 2>/dev/null || true)"
running_green="$("${COMPOSE[@]}" ps -q web-green 2>/dev/null || true)"

if [[ -z "$running_blue" && -z "$running_green" ]]; then
  CURRENT=none
  NEXT=blue
elif grep -q 'web-green' "$UPSTREAM_FILE"; then
  CURRENT=green
  NEXT=blue
else
  CURRENT=blue
  NEXT=green
fi
echo "==> current color: $CURRENT  ->  deploying: $NEXT"

# Pull + start the idle color. The running color keeps serving unchanged.
"${COMPOSE[@]}" pull "web-$NEXT" nginx
"${COMPOSE[@]}" up -d --no-deps "web-$NEXT"

# Wait for the new color's Docker healthcheck (hits /healthz, which pings DB).
echo "==> waiting for web-$NEXT to become healthy (timeout ${HEALTH_TIMEOUT}s)"
elapsed=0
container_id=""
while [[ $elapsed -lt $HEALTH_TIMEOUT ]]; do
  container_id="$("${COMPOSE[@]}" ps -q "web-$NEXT" || true)"
  if [[ -n "$container_id" ]]; then
    status="$(docker inspect --format '{{.State.Health.Status}}' "$container_id" 2>/dev/null || echo "starting")"
    if [[ "$status" == "healthy" ]]; then
      echo "==> web-$NEXT is healthy"
      break
    fi
  fi
  sleep 2
  elapsed=$((elapsed + 2))
done

if [[ "$(docker inspect --format '{{.State.Health.Status}}' "$container_id" 2>/dev/null || echo missing)" != "healthy" ]]; then
  echo "!! web-$NEXT did not become healthy within ${HEALTH_TIMEOUT}s; keeping web-$CURRENT live" >&2
  "${COMPOSE[@]}" logs --tail=80 "web-$NEXT" >&2 || true
  "${COMPOSE[@]}" stop "web-$NEXT" >&2 || true
  exit 1
fi

# Point nginx at the new color and graceful-reload (drains in-flight requests).
echo "==> swapping nginx upstream -> web-$NEXT"
sed -i "s/web-[a-z]\+:8000/web-$NEXT:8000/" "$UPSTREAM_FILE"

# Bring nginx in line with the committed compose config BEFORE validating.
# When the nginx mounts or config change (e.g. the upstream moved into its own
# mounted directory), the running container still has the old mounts while the
# bind-mounted conf.d already shows the new app.conf — so `nginx -t` inside the
# old container fails on an include path it can't see yet. `up -d` recreates
# the container in that case (picking up the new mounts); when nothing changed
# it's a no-op and we simply graceful-reload to read the new upstream file.
"${COMPOSE[@]}" up -d --no-deps nginx
"${COMPOSE[@]}" exec -T nginx nginx -t
"${COMPOSE[@]}" exec -T nginx nginx -s reload

# Drain briefly, then stop the outgoing color.
sleep 3
if [[ "$CURRENT" != "none" ]]; then
  echo "==> stopping web-$CURRENT"
  "${COMPOSE[@]}" stop "web-$CURRENT"
fi

echo "==> deploy complete: live color is web-$NEXT"
