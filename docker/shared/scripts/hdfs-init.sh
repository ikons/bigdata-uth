#!/usr/bin/env bash

set -euo pipefail

MAX_ATTEMPTS="${MAX_ATTEMPTS:-60}"
SLEEP_SECONDS="${SLEEP_SECONDS:-2}"
HDFS_URI="${HDFS_URI:-hdfs://namenode:9000}"
HDFS_BIN="${HDFS_BIN:-/opt/hadoop-3.2.1/bin/hdfs}"

hdfs_cmd() {
  "${HDFS_BIN}" "$@"
}

wait_for_hdfs_rpc() {
  local attempt
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    if hdfs_cmd dfsadmin -fs "${HDFS_URI}" -report >/dev/null 2>&1; then
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
    safe_mode_output="$(hdfs_cmd dfsadmin -fs "${HDFS_URI}" -safemode get 2>/dev/null || true)"
    echo "safe mode attempt ${attempt}/${MAX_ATTEMPTS}: ${safe_mode_output:-unknown}"
    if ! printf '%s' "$safe_mode_output" | grep -q 'Safe mode is ON'; then
      return 0
    fi
    sleep "$SLEEP_SECONDS"
  done

  echo "HDFS stayed in safe mode for too long." >&2
  return 1
}

echo "Waiting for the HDFS RPC endpoint to respond..."
wait_for_hdfs_rpc

# Ask HDFS to leave safe mode when it is already ready enough to accept admin commands.
# If it has already left safe mode, this is a harmless no-op.
hdfs_cmd dfsadmin -fs "${HDFS_URI}" -safemode leave >/dev/null 2>&1 || true

echo "Waiting for HDFS safe mode to end..."
wait_for_safe_mode_to_end

# -mkdir -p makes the bootstrap idempotent. Re-running it repairs the expected
# lab directories without requiring manual cleanup of the whole stack.
echo "Creating the lab directories in HDFS..."
hdfs_cmd dfs -fs "${HDFS_URI}" -mkdir -p /user/root /user/root/examples /logs

echo "HDFS bootstrap completed."
