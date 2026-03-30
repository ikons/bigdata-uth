FROM apache/spark:3.5.8-scala2.12-java11-python3-ubuntu

USER root

# The History Server is a separate reusable image. The log source is provided
# at runtime through environment variables and mounted Hadoop config files.
COPY docker/images/spark-history/history-server.sh /history-server.sh
RUN chmod +x /history-server.sh

RUN mkdir -p /opt/spark/conf /opt/spark/logs

EXPOSE 18081

CMD ["/bin/bash", "-c", "/history-server.sh"]
