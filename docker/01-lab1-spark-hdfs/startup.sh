#!/usr/bin/env bash

set -eo pipefail

# Tell helper scripts where Spark is installed inside the image.
export SPARK_HOME=/opt/spark
. "/opt/spark/sbin/spark-config.sh"
. "/opt/spark/bin/load-spark-env.sh"

# The master and the History Server both write logs under the same directory.
mkdir -p "$SPARK_MASTER_LOG"
echo "SPARK_HISTORY_OPTS: $SPARK_HISTORY_OPTS"

# Redirect the main log file to stdout so `docker logs spark-master`
# shows both the master process and the History Server output.
ln -sf /dev/stdout "$SPARK_MASTER_LOG/spark-master.out"

cd /opt/spark/bin

run_history_server_forever() {
  while true; do
    echo "Starting History Server..." >> "$SPARK_MASTER_LOG/spark-master.out"
    /opt/spark/sbin/../bin/spark-class org.apache.spark.deploy.history.HistoryServer \
      >> "$SPARK_MASTER_LOG/spark-master.out" 2>&1 || true
    echo "History Server exited. Retrying in 5 seconds..." >> "$SPARK_MASTER_LOG/spark-master.out"
    sleep 5
  done
}

# Start the standalone Spark master. Workers discover it through the
# hostname `spark-master`, which Docker Compose resolves on the shared network.
/opt/spark/sbin/../bin/spark-class org.apache.spark.deploy.master.Master \
  --ip "$SPARK_MASTER_HOST" \
  --port "$SPARK_MASTER_PORT" \
  --webui-port "$SPARK_MASTER_WEBUI_PORT" >> "$SPARK_MASTER_LOG/spark-master.out" &

# Start the History Server in the same container. It reads event logs from HDFS
# so students can inspect completed jobs even after executors have finished.
# The loop makes the service resilient to short HDFS startup races.
run_history_server_forever &

# Keep the container alive as long as the background Spark services are running.
wait
