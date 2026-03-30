#!/usr/bin/env bash

set -eo pipefail

export SPARK_HOME=/opt/spark
. "/opt/spark/sbin/spark-config.sh"
. "/opt/spark/bin/load-spark-env.sh"

: "${SPARK_HISTORY_LOG_DIR:?Set SPARK_HISTORY_LOG_DIR to the HDFS path that contains Spark event logs.}"

SPARK_HISTORY_UI_PORT="${SPARK_HISTORY_UI_PORT:-18081}"
SPARK_DAEMON_MEMORY="${SPARK_DAEMON_MEMORY:-1g}"
export SPARK_DAEMON_MEMORY

export SPARK_HISTORY_OPTS="${SPARK_HISTORY_OPTS:-} -Dspark.history.fs.logDirectory=${SPARK_HISTORY_LOG_DIR} -Dspark.history.ui.port=${SPARK_HISTORY_UI_PORT}"

# Redirect the History Server log to stdout so `docker logs` stays enough for diagnostics.
ln -sf /dev/stdout /opt/spark/logs/spark-history.out

while true; do
  echo "Starting History Server for logs at ${SPARK_HISTORY_LOG_DIR}" >> /opt/spark/logs/spark-history.out
  /opt/spark/bin/spark-class org.apache.spark.deploy.history.HistoryServer \
    >> /opt/spark/logs/spark-history.out 2>&1 || true
  echo "History Server exited. Retrying in 5 seconds..." >> /opt/spark/logs/spark-history.out
  sleep 5
done
