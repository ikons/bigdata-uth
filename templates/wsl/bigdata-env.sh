# Shared Spark/Hadoop/Kubernetes environment for the lab WSL setup.
# Default baseline: Spark 3.5.8 + Hadoop client 3.4.1 + Java 11.
#
# This file is sourced by interactive shells. Keep top-level code idempotent:
# exports and function definitions are safe, but setup actions should happen
# only when you call an explicit helper function.

# Change this one line to the username assigned by the vdcloud lab.
export VDCLOUD_USER="your_vdcloud_username"

export SPARK_HOME="$HOME/spark-3.5.8-bin-hadoop3"
export HADOOP_HOME="$HOME/hadoop-3.4.1"
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export SPARK_CONF_DIR="$HOME/.spark/conf"
export HADOOP_CONF_DIR="$HOME/.hadoop/conf"
export PATH="$HOME/.local/bin:$SPARK_HOME/bin:$HADOOP_HOME/bin:$PATH"
export KUBE_EDITOR=nano
export HADOOP_USER_NAME="$VDCLOUD_USER"
export HADOOP_ROOT_LOGGER=ERROR,console

bigdata_require_vdcloud_user() {
    local placeholder
    placeholder="$(printf '%s_%s_%s' your vdcloud username)"

    if [ -z "${VDCLOUD_USER:-}" ] || [ "$VDCLOUD_USER" = "$placeholder" ]; then
        echo "Set VDCLOUD_USER in ~/bigdata-env.sh first." >&2
        return 1
    fi
}

bigdata_write_spark_defaults() {
    # Spark does not expand shell variables inside spark-defaults.conf.
    # Generate the file from VDCLOUD_USER so the final config is explicit
    # and easy to inspect when debugging a failed submit.
    bigdata_require_vdcloud_user || return 1

    mkdir -p "$SPARK_CONF_DIR"

    cat > "$SPARK_CONF_DIR/spark-defaults.conf" <<EOF
# Generated from ~/bigdata-env.sh for VDCLOUD_USER=${VDCLOUD_USER}.

spark.master                                   k8s://https://source-code-master.cluster.local:6443
spark.submit.deployMode                        cluster
spark.kubernetes.namespace                     ${VDCLOUD_USER}-priv
spark.kubernetes.authenticate.driver.serviceAccountName spark
spark.kubernetes.container.image               apache/spark:3.5.8-scala2.12-java11-python3-ubuntu
spark.executor.instances                       1
spark.kubernetes.submission.waitAppCompletion  false
spark.kubernetes.driverEnv.HADOOP_USER_NAME    ${VDCLOUD_USER}
spark.executorEnv.HADOOP_USER_NAME             ${VDCLOUD_USER}
spark.kubernetes.file.upload.path              hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/${VDCLOUD_USER}/.spark-upload
spark.eventLog.enabled                         true
spark.eventLog.dir                             hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/${VDCLOUD_USER}/logs
spark.history.fs.logDirectory                  hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/${VDCLOUD_USER}/logs
EOF

    echo "Wrote $SPARK_CONF_DIR/spark-defaults.conf"
}

bigdata_write_history_env() {
    # The standalone History Server is a Docker stack. It also needs the same
    # HDFS identity, because each student's event logs are private.
    bigdata_require_vdcloud_user || return 1

    local stack_dir="${1:-$HOME/bigdata-uth/docker/stacks/history-server-lab}"
    if [ ! -d "$stack_dir" ]; then
        echo "History Server stack not found: $stack_dir" >&2
        return 1
    fi

    cat > "$stack_dir/.env" <<EOF
SPARK_HISTORY_UI_HOST_PORT=18081
HADOOP_USER_NAME=${VDCLOUD_USER}
SPARK_HISTORY_LOG_DIR=hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/${VDCLOUD_USER}/logs
EOF

    echo "Wrote $stack_dir/.env"
}
