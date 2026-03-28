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

# Start the standalone Spark master. Workers discover it through the
# hostname `spark-master`, which Docker Compose resolves on the shared network.
/opt/spark/sbin/../bin/spark-class org.apache.spark.deploy.master.Master \
  --ip "$SPARK_MASTER_HOST" \
  --port "$SPARK_MASTER_PORT" \
  --webui-port "$SPARK_MASTER_WEBUI_PORT" >> "$SPARK_MASTER_LOG/spark-master.out" &

# Start the History Server in the same container. It reads event logs from HDFS
# so students can inspect completed jobs even after executors have finished.
/opt/spark/sbin/../bin/spark-class org.apache.spark.deploy.history.HistoryServer \
  >> "$SPARK_MASTER_LOG/spark-master.out" &

# Keep the container alive as long as the background Spark services are running.
wait
