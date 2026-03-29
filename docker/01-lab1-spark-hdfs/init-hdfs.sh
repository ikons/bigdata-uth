#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MAX_ATTEMPTS=60
SLEEP_SECONDS=2

wait_for_namenode_health() {
  local attempt health
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    health="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' namenode 2>/dev/null || true)"
    echo "namenode health attempt ${attempt}/${MAX_ATTEMPTS}: ${health}"
    if [ "$health" = "healthy" ]; then
      return 0
    fi
    sleep "$SLEEP_SECONDS"
  done

  echo "NameNode did not become healthy in time." >&2
  return 1
}

wait_for_hdfs_rpc() {
  local attempt
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    if docker exec namenode hdfs dfsadmin -report >/dev/null 2>&1; then
      echo "HDFS RPC endpoint is responding."
      return 0
    fi
    echo "HDFS RPC attempt ${attempt}/${MAX_ATTEMPTS}: not ready yet"
    sleep "$SLEEP_SECONDS"
  done

  echo "HDFS RPC endpoint did not become ready in time." >&2
  return 1
}

wait_for_safe_mode_to_end() {
  local attempt safe_mode_output
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    safe_mode_output="$(docker exec namenode hdfs dfsadmin -safemode get 2>/dev/null || true)"
    echo "safe mode attempt ${attempt}/${MAX_ATTEMPTS}: ${safe_mode_output:-unknown}"
    if ! printf '%s' "$safe_mode_output" | grep -q 'Safe mode is ON'; then
      return 0
    fi
    sleep "$SLEEP_SECONDS"
  done

  echo "HDFS stayed in safe mode for too long." >&2
  return 1
}

echo "Waiting for the NameNode container to become healthy..."
wait_for_namenode_health

echo "Waiting for the HDFS RPC endpoint to respond..."
wait_for_hdfs_rpc

# Ask HDFS to leave safe mode when it is already ready enough to accept admin commands.
# If it has already left safe mode, this is a harmless no-op.
docker exec namenode hdfs dfsadmin -safemode leave >/dev/null 2>&1 || true

echo "Waiting for HDFS safe mode to end..."
wait_for_safe_mode_to_end

echo "Creating the lab directories in HDFS..."
docker exec namenode hdfs dfs -mkdir -p /user/root /user/root/examples /logs

echo "Restarting spark-master so the History Server reconnects to the ready HDFS..."
docker compose restart spark-master

echo "Local HDFS initialization completed."
