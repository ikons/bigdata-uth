FROM apache/spark:latest

# Αντιγραφή αρχείων Hadoop configuration
COPY core-site.xml /opt/spark/conf/core-site.xml
COPY hdfs-site.xml /opt/spark/conf/hdfs-site.xml

# Αναμενόμενη μεταβλητή: USERNAME
ENV USERNAME=

# Εκκίνηση με έλεγχο USERNAME και κατασκευή του LOG_DIR
ENTRYPOINT ["/bin/bash", "-c", "\
  if [ -z \"$USERNAME\" ]; then \
    echo 'ERROR: Πρέπει να ορίσετε USERNAME (π.χ. -e USERNAME=ikons)' >&2; \
    exit 1; \
  fi; \
  export LOG_DIR=hdfs://hdfs-namenode:9000/user/$USERNAME/logs; \
  export SPARK_HISTORY_OPTS=\"-Dspark.history.fs.logDirectory=$LOG_DIR \
                             -Dspark.history.fs.cleaner.enabled=true \
                             -Dspark.history.ui.port=18080\"; \
  echo \"Ξεκινάει το Spark History Server για τον χρήστη $USERNAME, logs από $LOG_DIR\"; \
  exec /opt/spark/bin/spark-class org.apache.spark.deploy.history.HistoryServer"]

