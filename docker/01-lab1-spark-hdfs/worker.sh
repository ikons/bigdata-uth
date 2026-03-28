#!/usr/bin/env bash

set -eo pipefail

# Tell helper scripts where Spark is installed inside the image.
export SPARK_HOME=/opt/spark
. "/opt/spark/sbin/spark-config.sh"
. "/opt/spark/bin/load-spark-env.sh"

# Create the worker log directory expected by Spark.
mkdir -p "$SPARK_WORKER_LOG"

# Redirect worker output to stdout so it is visible through `docker logs`.
ln -sf /dev/stdout "$SPARK_WORKER_LOG/spark-worker.out"

# Register this container as a worker of the standalone master.
# The value of SPARK_MASTER comes from docker-compose.yml and points to
# the master service by its Docker network hostname.
/opt/spark/sbin/../bin/spark-class org.apache.spark.deploy.worker.Worker \
  --webui-port "$SPARK_WORKER_WEBUI_PORT" \
  "$SPARK_MASTER" >> "$SPARK_WORKER_LOG/spark-worker.out"
