#!/bin/bash
export SPARK_HOME=/opt/spark
. "/opt/spark/sbin/spark-config.sh"
. "/opt/spark/bin/load-spark-env.sh"
mkdir -p $SPARK_MASTER_LOG
echo "SPARK_HISTORY_OPTS: " $SPARK_HISTORY_OPTS
ln -sf /dev/stdout $SPARK_MASTER_LOG/spark-master.out
cd /opt/spark/bin
/opt/spark/sbin/../bin/spark-class org.apache.spark.deploy.master.Master --ip $SPARK_MASTER_HOST --port $SPARK_MASTER_PORT --webui-port $SPARK_MASTER_WEBUI_PORT >> $SPARK_MASTER_LOG/spark-master.out &
/opt/spark/sbin/../bin/spark-class org.apache.spark.deploy.history.HistoryServer >> $SPARK_MASTER_LOG/spark-master.out &
wait
