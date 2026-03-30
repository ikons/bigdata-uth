#!/usr/bin/env bash

set -eo pipefail

export SPARK_HOME=/opt/spark
. "/opt/spark/sbin/spark-config.sh"
. "/opt/spark/bin/load-spark-env.sh"

# Start a standalone worker that connects to the master service discovered
# through the shared Docker network.
/opt/spark/sbin/start-worker.sh "$SPARK_MASTER"

# Keep the container alive by streaming the Spark worker log to stdout.
tail -f /opt/spark/logs/spark--org.apache.spark.deploy.worker.Worker-1-*.out
