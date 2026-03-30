FROM apache/spark:3.5.8-scala2.12-java11-python3-ubuntu

# Use root so the image can copy the startup script and shared Spark defaults.
USER root

COPY docker/images/spark-worker/worker.sh /worker.sh
RUN chmod +x /worker.sh

RUN mkdir -p /opt/spark/conf
COPY docker/shared/spark/spark-defaults.conf /opt/spark/conf/spark-defaults.conf

CMD ["/bin/bash", "-c", "/worker.sh"]
