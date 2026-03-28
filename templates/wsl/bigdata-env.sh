# Shared Spark/Hadoop/Kubernetes environment for the lab WSL setup.
# Default baseline: Spark 3.5.8 + Hadoop client 3.4.1 + Java 11.

export SPARK_HOME="$HOME/spark-3.5.8-bin-hadoop3"
export HADOOP_HOME="$HOME/hadoop-3.4.1"
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export SPARK_CONF_DIR="$HOME/.spark/conf"
export HADOOP_CONF_DIR="$HOME/.hadoop/conf"
export PATH="$HOME/.local/bin:$SPARK_HOME/bin:$HADOOP_HOME/bin:$PATH"
export KUBE_EDITOR=nano
export HADOOP_USER_NAME="$USER"
