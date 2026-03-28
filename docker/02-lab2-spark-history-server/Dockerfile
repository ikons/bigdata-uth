FROM apache/spark:3.5.8-scala2.12-java11-python3-ubuntu

# Copy the Hadoop client configuration that lets the History Server
# read Spark event logs directly from the lab HDFS cluster.
COPY core-site.xml /opt/spark/conf/core-site.xml
COPY hdfs-site.xml /opt/spark/conf/hdfs-site.xml

# The container is parameterized per student. At runtime we expect
# USERNAME to match the HDFS home directory that stores the event logs.
ENV USERNAME=

# Build the HDFS log directory from USERNAME and start the History Server.
# Keeping this logic in ENTRYPOINT makes the image reusable for any user.
ENTRYPOINT ["/bin/bash", "-c", "\
  if [ -z \"$USERNAME\" ]; then \
    echo 'ERROR: You must set USERNAME (for example: -e USERNAME=ikons)' >&2; \
    exit 1; \
  fi; \
  export LOG_DIR=hdfs://hdfs-namenode:9000/user/$USERNAME/logs; \
  export SPARK_HISTORY_OPTS=\"-Dspark.history.fs.logDirectory=$LOG_DIR \
                             -Dspark.history.fs.cleaner.enabled=true \
                             -Dspark.history.ui.port=18080\"; \
  echo \"Starting the Spark History Server for user $USERNAME, reading logs from $LOG_DIR\"; \
  exec /opt/spark/bin/spark-class org.apache.spark.deploy.history.HistoryServer"]

