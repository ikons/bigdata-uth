FROM apache/spark:3.5.8-scala2.12-java11-python3-ubuntu

# Use root so the image can copy startup scripts and write Spark config files.
USER root

# This image is responsible only for the standalone Spark master process.
COPY docker/images/spark-master/startup.sh /startup.sh
RUN chmod +x /startup.sh

# Every Spark container in the local stack reads the same defaults file so that
# they all agree on the master URL and the HDFS-backed event log location.
RUN mkdir -p /opt/spark/conf
COPY docker/shared/spark/spark-defaults.conf /opt/spark/conf/spark-defaults.conf

ENV SPARK_MASTER_PORT=7077
ENV SPARK_MASTER_WEBUI_PORT=8080
ENV SPARK_MASTER_LOG=/opt/spark/logs

EXPOSE 8080 7077 6066

CMD ["/bin/bash", "-c", "/startup.sh"]
