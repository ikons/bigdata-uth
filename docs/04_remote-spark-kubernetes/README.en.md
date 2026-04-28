# Remote Spark execution on Kubernetes from WSL

This guide comes after local development and before the guide for [the same queries on the cluster](../05_cluster-queries-rdd-df-sql/README.en.md).

The goal here is not to learn a new Spark API. The goal is to build a stable workflow in WSL where:

- local development happens in VS Code or PyCharm
- remote submission happens from the student's own WSL through the lab VPN
- the Kubernetes cluster is already provided by the lab
- `spark-submit`, `kubectl`, and `hdfs` work from the same environment

This guide runs only from WSL. A native Windows path would be possible in theory, but it is intentionally not documented in the course because the workflow depends on `spark-submit`, `hdfs`, `kubectl`, `~/.kube`, `~/.spark`, `~/.hadoop`, and a Linux-style shell environment in general.

## Recommended versions

The recommended software baseline for the course is:

| Component | Recommended baseline |
| --- | --- |
| Java in WSL | `OpenJDK 11` |
| Spark client in WSL | `spark-3.5.8-bin-hadoop3` |
| Hadoop client in WSL | `hadoop-3.4.1` |
| Spark image on Kubernetes | `apache/spark:3.5.8-scala2.12-java11-python3-ubuntu` |
| HDFS server on vdcloud | `3.4.1` |

In other words, the course baseline is:

- `Spark 3.5.8`
- `Java 11`
- `Hadoop client 3.4.1`
- pinned image `apache/spark:3.5.8-scala2.12-java11-python3-ubuntu`

## What you need before you start

- WSL 2 with Ubuntu
- the lab VPN profile
- the lab kubeconfig
- cloned repository `~/bigdata-uth`
- Java, a Spark client, and a Hadoop client inside WSL
- a personal namespace `<username>-priv`
- a `spark` service account inside that namespace

The installation steps for `OpenVPN`, `kubectl`, and the initial `~/.kube/config` are already covered in [01_workstation-setup](../01_workstation-setup/README.en.md). From this point on, we assume the VPN is already connected and that `kubectl config current-context` already works.

## 1. Check Java, Spark, and Hadoop in WSL

The baseline WSL installation belongs in `01_workstation-setup`. If this is your first pass through this guide, go to step `2` first, create the shared `~/bigdata-env.sh` file, and then return here.

If the environment is already in place, load it first and then verify that the expected binaries are visible.

```bash
. ~/.profile
java -version
command -v spark-submit
command -v hdfs
spark-submit --version
hadoop version
```

If any of the above is missing, go back to `01_workstation-setup` first and complete the installation of `Spark 3.5.8` and the `Hadoop client 3.4.1`.

## 2. Shared environment file in WSL

Keep the paths in one shared file, not scattered across `~/.bashrc`.

```bash
cd ~/bigdata-uth
mkdir -p ~/.spark/conf ~/.hadoop/conf
cp templates/wsl/bigdata-env.sh ~/bigdata-env.sh
nano ~/bigdata-env.sh
```

At the top of the file, change only this line:

```bash
export VDCLOUD_USER="your_vdcloud_username"
```

and set the username assigned by the lab, for example:

```bash
export VDCLOUD_USER="ikons"
```

You do not need to copy this by hand. For reference, the copied file contains:

<!-- AUTO-CODE: templates/wsl/bigdata-env.sh -->
``` bash
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
```
<!-- END AUTO-CODE -->

> **Important:** `VDCLOUD_USER` may differ from your WSL Linux username and is used for HDFS paths and Kubernetes namespaces.

### Activating the environment in every new shell

Bash reads a different startup file depending on how a shell is opened:

- `~/.profile` — read once when a **login shell** starts (each time WSL opens). Environment variables set here are inherited by child processes, including those launched by `spark-submit`.
- `~/.bashrc` — read for each new **interactive shell** (for example, every time you open a new terminal tab).

To make `bigdata-env.sh` load automatically in both cases, run:

```bash
echo '. ~/bigdata-env.sh' >> ~/.profile
echo '. ~/bigdata-env.sh' >> ~/.bashrc
```

The `>>` operator **appends** one line to the file without overwriting anything. The `.` is shorthand for `source` — it executes the named file inside the current shell.

> **Run each command exactly once.** Running either command a second time appends a duplicate line. If that happens, open the file with `nano ~/.profile` or `nano ~/.bashrc` and delete the extra line.

Apply the changes to the current session without restarting:

```bash
. ~/.profile
```

and verify:

```bash
deactivate 2>/dev/null || true
source ~/bigdata-env.sh
hash -r
command -v spark-submit
command -v hdfs
java -version
spark-submit --version
hadoop version
```

`command -v spark-submit` must point to the WSL Spark install, for example `/home/$USER/spark-3.5.8-bin-hadoop3/bin/spark-submit`. If it points to `.venv/bin/spark-submit`, you are still on the local Python path and the submit will not go to the Kubernetes cluster as expected.

## 3. kubeconfig, kubectl, and DNS

Place the kubeconfig at:

```bash
mkdir -p ~/.kube
cp /path/to/config ~/.kube/config
```

Then verify:

```bash
kubectl config current-context
kubectl config get-contexts
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}{"\n"}'
```

The Kubernetes API endpoint must not be copied from stale screenshots. It must come from the kubeconfig provided by the lab.

In the current lab setup, the correct internal DNS name is `source-code-master.cluster.local`, but the kubeconfig remains the source of truth.

For the WSL path, also verify DNS and HDFS reachability:

```bash
getent hosts source-code-master.cluster.local
getent hosts hdfs-namenode.default.svc.cluster.local
kubectl -n "$VDCLOUD_USER-priv" get sa spark
```

## 4. Configure the Hadoop client

Keep the HDFS config in a per-user path instead of modifying the unpacked binaries.

```bash
cd ~/bigdata-uth
mkdir -p ~/.hadoop/conf
cp templates/wsl/core-site.xml ~/.hadoop/conf/core-site.xml
cp templates/wsl/log4j.properties ~/.hadoop/conf/log4j.properties
```

The `core-site.xml` file contains:

<!-- AUTO-CODE: templates/wsl/core-site.xml -->
``` xml
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://hdfs-namenode.default.svc.cluster.local:9000</value>
  </property>
</configuration>
```
<!-- END AUTO-CODE -->

If the lab also provides an `hdfs-site.xml`, place it inside `~/.hadoop/conf/` as well.

The `log4j.properties` file is only there to stop every `hdfs` command from printing the `log4j.properties is not found` warning.

Then verify:

```bash
hdfs dfs -ls /
hdfs dfs -ls /user/$VDCLOUD_USER
```

## 5. Per-user `spark-defaults.conf`

The most practical setup for students is to make Kubernetes cluster mode the default for `spark-submit` inside WSL.

`spark-defaults.conf` must contain real values, not shell variables. Generate it from the `VDCLOUD_USER` value you already set in `~/bigdata-env.sh`:

```bash
source ~/bigdata-env.sh
bigdata_write_spark_defaults
cat ~/.spark/conf/spark-defaults.conf
```

The helper function writes the following template with your vdcloud username:

<!-- AUTO-CODE: templates/wsl/spark-defaults.conf -->
``` properties
# Example output written by bigdata_write_spark_defaults.
# The real file contains your actual VDCLOUD_USER value.

spark.master                                   k8s://https://source-code-master.cluster.local:6443
spark.submit.deployMode                        cluster
spark.kubernetes.namespace                     VDCLOUD_USER-priv
spark.kubernetes.authenticate.driver.serviceAccountName spark
spark.kubernetes.container.image               apache/spark:3.5.8-scala2.12-java11-python3-ubuntu
spark.executor.instances                       1
spark.kubernetes.submission.waitAppCompletion  false
spark.kubernetes.driverEnv.HADOOP_USER_NAME    VDCLOUD_USER
spark.executorEnv.HADOOP_USER_NAME             VDCLOUD_USER
spark.kubernetes.file.upload.path              hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/VDCLOUD_USER/.spark-upload
spark.eventLog.enabled                         true
spark.eventLog.dir                             hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/VDCLOUD_USER/logs
spark.history.fs.logDirectory                  hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/VDCLOUD_USER/logs
```
<!-- END AUTO-CODE -->

Before the first submit:

- check that the file contains your vdcloud username
- make sure `spark.master` matches the kubeconfig
- keep the image pinned instead of using plain `apache/spark`
- keep the three `HADOOP_USER_NAME` and `spark.kubernetes.file.upload.path` settings, because HDFS home directories are private

## 6. Check your private HDFS workspace

From the repository root:

```bash
cd ~/bigdata-uth
hdfs dfs -ls -d /user/$VDCLOUD_USER
hdfs dfs -ls -d /user/$VDCLOUD_USER/.spark-upload
hdfs dfs -ls -d /user/$VDCLOUD_USER/logs
```

The `/user/$VDCLOUD_USER`, `.spark-upload`, and `logs` directories are created by the lab when your account is provisioned. They should already exist and be private. If any of them is missing, do not change permissions yourself; notify the instructor.

For this guide's examples, upload only the data:

```bash
hdfs dfs -mkdir -p /user/$VDCLOUD_USER/examples
hdfs dfs -chmod 700 /user/$VDCLOUD_USER/examples
hdfs dfs -put -f examples/* /user/$VDCLOUD_USER/examples/
hdfs dfs -ls /user/$VDCLOUD_USER/examples
```

Do not upload `code/*.py` to HDFS. Keep scripts local in WSL and let Spark stage them temporarily under the private `/user/$VDCLOUD_USER/.spark-upload` directory when you pass them to `spark-submit`.

## 7. First `spark-submit`

Once `spark-defaults.conf` is configured, the first submit becomes very simple:

```bash
spark-submit code/wordcount.py \
  --base-path hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/$VDCLOUD_USER
```

The canonical code for the example is:

<!-- AUTO-CODE: code/wordcount.py -->
``` python
from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession

# Keep the Python executable the same on the driver and on Spark workers.
# This avoids subtle version mismatches when the same script runs locally or on a cluster.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def build_path(base_path: str, relative_path: str) -> str:
    return f"{base_path.rstrip('/')}/{relative_path.lstrip('/')}"


def write_local_text_output(output_path: str, lines: list[str]) -> None:
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "part-00000")
    with open(output_file, "w", encoding="utf-8") as file_handle:
        for line in lines:
            file_handle.write(f"{line}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count word frequencies from a text file with Spark.",
    )
    parser.add_argument(
        "--base-path",
        help="Base path that contains examples/ and where outputs should be written.",
    )
    parser.add_argument(
        "--input",
        help="Explicit input text path. Defaults to examples/text.txt locally or <base-path>/examples/text.txt remotely.",
    )
    parser.add_argument(
        "--output",
        help="Explicit output path. If omitted, local runs only print results and remote runs write under <base-path>.",
    )
    parser.add_argument(
        "--master",
        help="Optional Spark master. Local runs default to local[*] when no remote path is used.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input or (
        build_path(args.base_path, "examples/text.txt")
        if args.base_path
        else "examples/text.txt"
    )

    builder = SparkSession.builder.appName("wordcount example")
    # Reuse the same script in two contexts:
    # - local files -> start a local Spark session
    # - remote URIs -> let spark-submit use the external cluster configuration
    if args.master:
        builder = builder.master(args.master)
        if args.master.startswith("local"):
            builder = builder.config("spark.submit.deployMode", "client")
    elif "://" not in input_path:
        builder = builder.master("local[*]").config("spark.submit.deployMode", "client")

    spark = builder.getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    output_path = args.output
    if output_path is None and args.base_path:
        output_path = build_path(args.base_path, f"wordcount_output_{sc.applicationId}")

    wordcount = (
        # textFile() gives an RDD where each element is one line from the input file.
        sc.textFile(input_path)
        # flatMap() is the classic "one input record -> many output records" step.
        .flatMap(lambda line: line.split())
        .map(lambda word: (word, 1))
        # reduceByKey() is the standard RDD aggregation pattern for key-value data.
        .reduceByKey(lambda left, right: left + right)
        .sortBy(lambda item: (-item[1], item[0]))
    )

    # collect() is safe here because the lab output is intentionally small.
    results = wordcount.collect()
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # coalesce(1) makes the lab output easier to inspect.
            # For large real workloads, a single output partition would usually be a bottleneck.
            wordcount.coalesce(1).saveAsTextFile(output_path)
        else:
            write_local_text_output(output_path, [str(item) for item in results])
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
```
<!-- END AUTO-CODE -->

## 8. Monitoring the execution

After submission:

```bash
kubectl -n "$VDCLOUD_USER-priv" get pods -o wide
kubectl -n "$VDCLOUD_USER-priv" logs <driver-pod-name>
kubectl -n "$VDCLOUD_USER-priv" describe pod <driver-pod-name>
```

If you use `k9s`:

```bash
k9s -n "$VDCLOUD_USER-priv"
```

Then check output and event logs:

```bash
hdfs dfs -ls /user/$VDCLOUD_USER | grep wordcount_output
hdfs dfs -ls /user/$VDCLOUD_USER/logs | tail -n 5
hdfs dfs -ls /user/$VDCLOUD_USER/.spark-upload
```

When no job for your user is running, you can remove temporary staged scripts:

```bash
hdfs dfs -rm -r -skipTrash /user/$VDCLOUD_USER/.spark-upload/spark-upload-* 2>/dev/null || true
```

### Local History Server for remote logs

To inspect vdcloud event logs through a local Spark History Server:

```bash
cd ~/bigdata-uth/docker/stacks/history-server-lab
source ~/bigdata-env.sh
bigdata_write_history_env
cat .env
```

The `.env` file must contain your own values:

```env
SPARK_HISTORY_UI_HOST_PORT=18081
HADOOP_USER_NAME=VDCLOUD_USER
SPARK_HISTORY_LOG_DIR=hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/VDCLOUD_USER/logs
```

Then start the History Server:

```bash
docker compose up --build -d
curl http://localhost:18081/api/v1/applications
```

`HADOOP_USER_NAME` is required because `/user/<username>/logs` is private in HDFS.

## Troubleshooting

### `spark-submit` cannot find the paths

This usually means `bigdata-env.sh` was not loaded in the shell you are using.

Check:

```bash
echo "$SPARK_HOME"
echo "$HADOOP_HOME"
command -v spark-submit
command -v hdfs
```

### The job ran locally instead of on Kubernetes

This usually means `spark-defaults.conf` is missing or was not loaded.

Check:

```bash
spark-submit --version
test -f "$SPARK_CONF_DIR/spark-defaults.conf" && cat "$SPARK_CONF_DIR/spark-defaults.conf"
```

### Missing `spark.kubernetes.file.upload.path`

If `spark-submit code/wordcount.py` asks for `spark.kubernetes.file.upload.path`, Spark does not know where to stage the local script in HDFS. Run:

```bash
source ~/bigdata-env.sh
bigdata_write_spark_defaults
```

### `Permission denied` under `.spark-upload` or `logs`

Check that `~/.spark/conf/spark-defaults.conf` contains your username in all three relevant settings:

```properties
spark.kubernetes.driverEnv.HADOOP_USER_NAME VDCLOUD_USER
spark.executorEnv.HADOOP_USER_NAME VDCLOUD_USER
spark.kubernetes.file.upload.path hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/VDCLOUD_USER/.spark-upload
```

### Hostnames do not resolve from WSL

First check:

```bash
getent hosts source-code-master.cluster.local
getent hosts hdfs-namenode.default.svc.cluster.local
```

If these do not resolve, the problem is in the VPN or the WSL DNS path, not in the Spark script.

## What comes next

Once the first remote submit works, continue to the guide for [the same queries on the cluster](../05_cluster-queries-rdd-df-sql/README.en.md), where we run the same `Q1-Q3` questions with `RDD`, the `DataFrame API`, and `Spark SQL`.
