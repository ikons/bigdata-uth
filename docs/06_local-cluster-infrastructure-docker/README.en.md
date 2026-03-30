# Local Spark + HDFS cluster with Docker Compose

In this guide, students build a small but complete Spark + HDFS cluster from scratch on their own machine with Docker Compose. The goal is not only to run prepared examples, but also to understand which pieces are required for such an environment and how they work together.

As you go through the steps, you will see the role of the NameNode, the DataNodes, the Spark master, and the Spark workers in practice, initialize HDFS, upload code and data, and execute jobs on the cluster. The commands are documented for WSL so that the workflow stays consistent and simple throughout the lab.

This guide can run with two Docker variants inside WSL:

- **Recommended**: `Docker Desktop` with WSL integration
- **Optional advanced**: a native `Docker Engine` directly inside Ubuntu

Once `docker version` and `docker compose version` work normally from the WSL terminal, the main commands of the guide are the same for both paths.

## Docker preflight inside WSL

Before you continue, make sure the active Docker CLI inside WSL can talk to a working Docker daemon:

```bash
docker version
docker compose version
docker info --format '{{.ServerVersion}}'
```

If you use `Docker Desktop`, make sure the Windows application has fully started first.

If you use a native `Docker Engine` inside WSL, also verify:

```bash
systemctl is-active docker
```

which should return `active`.

## HDFS and Spark architecture

**HDFS** is a distributed file system from which Spark jobs can read and write data.

Cluster node roles:
![Figure 1](images/img1.png)

- **HDFS NameNode:** The NameNode is the most important HDFS node. It knows which DataNode stores each block of every file.
- **HDFS DataNode:** DataNodes store HDFS file blocks on their local file systems and serve those blocks when clients request them.

**Spark** is a unified distributed processing system for data analysis. It includes the Map/Reduce programming model as well as libraries for machine learning, SQL processing, and more.

![Figure 2](images/img2.png)

![Figure 3](images/img3.png)

- **Spark Master:** The Spark Master controls the available resources and launches/manages distributed applications across the cluster.
- **Spark Worker:** A Worker runs on each cluster node and manages the distributed tasks assigned to that node.
- **Spark Driver:** The Driver acts as the controller of a Spark application and maintains its overall execution state.

## Basic Docker concepts

To build the above infrastructure on a personal computer, we use Docker containers. The most important concepts are the following:

- **Docker image:** A static package that contains everything required to run an application, including code, dependencies, and runtime environment. To run a container, Docker first retrieves the corresponding image from an image repository. For example, the following command downloads and runs the official `hello-world` image:

```bash
docker run hello-world
```

- **Dockerfile:** A text file containing the instructions required to build a Docker image. It defines the base image, dependencies, and runtime configuration. The example below builds an image based on Python and runs a local `app.py` file.

Open the Ubuntu terminal and run:

```bash
mkdir compose-example
cd compose-example
```

Create a local `app.py` file:

```bash
nano app.py
```

Add the following content:

```python
print("Hello from Docker!")
```

Save the file (`CTRL+X`, then `Y`, then `Enter`).

Now create a local `Dockerfile`:

```bash
nano Dockerfile
```

Add the following content:

```dockerfile
FROM python:3.9
COPY app.py /app.py
CMD ["python", "/app.py"]
```

Save the file (`CTRL+X`, then `Y`, then `Enter`).

Build and run the image with the following commands:

```bash
docker build -t my-python-app .
```

![Figure 4](images/img4.png)

```bash
docker run my-python-app
```

To run the built image as a container, use the command above.

![Figure 5](images/img5.png)

The first time you run it, Docker downloads the required dependencies. On subsequent runs, this is no longer necessary.

- **Docker Compose:** A tool that manages multiple containers through a Compose file, defining services, networks, and persistent storage.
- Docker containers have an **ephemeral file system**, so data stored only inside the container is lost when the container is removed.
- **Volume:** A storage mechanism that lets containers preserve data even after restart or deletion. Docker uses **persistent volumes** for long-term storage. Volumes can be created, named, and mounted into containers.

## Installing Apache Spark and HDFS locally with Docker containers

Move to the example directory:

```bash
cd ~/bigdata-uth/docker/stacks/local-spark-hdfs/
```

Inside it you will find the following files:

- **compose.yml**: Creates a local infrastructure consisting of:
  - one HDFS cluster with one NameNode (`namenode`) and three DataNodes (`datanode1`, `datanode2`, `datanode3`)
  - one Spark cluster with one Master (`spark-master`) and four Workers (`spark-worker1`, `spark-worker2`, `spark-worker3`, `spark-worker4`)
  - one one-shot HDFS bootstrap service (`hdfs-init`)
  - one dedicated Spark History Server (`spark-history`)

This stack is built from shared Docker assets under the top-level `docker/` directory:

- `docker/images/spark-master/`: reusable image for `spark-master`
- `docker/images/spark-worker/`: reusable image for Spark workers
- `docker/images/spark-history/`: reusable image for the dedicated History Server
- `docker/shared/spark/spark-defaults.conf`: shared Spark configuration of the local stack
- `docker/shared/scripts/hdfs-init.sh`: one-shot HDFS bootstrap script
- `docker/shared/hadoop-conf/local-hdfs/`: Hadoop client configuration for the local HDFS
- `init-hdfs.sh`: optional host-side wrapper for manually rerunning `hdfs-init`

## How the services connect to each other

Before you start the commands, it is worth making the communication model of the local cluster explicit:

- All containers join the same Docker network, `hadoop-net`.
- Inside that network, the service names from `compose.yml` also act as hostnames.
- This means the Spark master reaches HDFS as `hdfs://namenode:9000`, and Spark workers reach the master as `spark://spark-master:7077`.
- Spark jobs are submitted from the `spark-master` container, but their input and output data live in the HDFS of the same stack.
- The one-shot `hdfs-init` service waits for HDFS and creates `/user/root`, `/user/root/examples`, and `/logs` automatically.
- The dedicated `spark-history` container reads Spark event logs from HDFS, so it can display completed applications even after the executors have finished.
- The named volumes preserve HDFS metadata, HDFS blocks, and temporary upload directories so they survive container restarts.

In other words:

- `namenode` and the `datanodes` form the HDFS subsystem
- `spark-master` and `spark-worker1-4` form the Spark cluster
- `spark-history` is a dedicated monitoring service and no longer runs inside `spark-master`
- the shared Docker network lets those two subsystems communicate through names such as `namenode` and `spark-master`
- `hdfs-init` prepares the required HDFS directory structure automatically
- HDFS is the shared storage layer used both by Spark jobs and by the History Server

**Starting the infrastructure:** Run the following command to launch the environment. **Important:** you must be inside `docker/stacks/local-spark-hdfs` for it to work correctly.

```bash
docker compose up --build -d
```

In this new version of the stack, HDFS initialization is performed automatically by the `hdfs-init` service. The main path of the guide no longer requires a manual `init-hdfs.sh` step after `docker compose up --build -d`.

The first execution may take several minutes, especially if the Docker daemon has just started or if the larger images still need to be downloaded. If it seems slow, first confirm that `docker version` works from inside the WSL terminal and give the Docker daemon a little time to finish its startup sequence.

If everything works correctly, the containers will start normally. If you use Docker Desktop, you will also see the stack in the graphical application (green dot).

![Figure 6](images/img6.png)

You can also list the containers from the terminal:

```bash
docker ps
```

![Figure 7](images/img7.png)

If you use Docker Desktop, click on **local-spark-hdfs** to see the individual containers.

![Figure 8](images/img8.png)

Whenever you see pairs of numbers such as `9870:9870`, it means that the container exposes a **service** (usually an HTTP site, but not necessarily). This service is **accessible from your host operating system**, either by clicking the link directly or by opening it in a browser.

For example, the `namenode` container serves:

http://localhost:9870

![Figure 9](images/img9.png)

And `spark-master` serves the Spark UI at:
- http://localhost:18080
- http://localhost:18081 for the dedicated History Server (`spark-history`)

The stack uses ports `18080` and `18081` instead of `8080` and `8081`, because on many Windows + WSL setups the lower ports are already reserved by the virtualization/networking stack and are not forwarded reliably to `localhost`.

![Figure 10](images/img10.png)

In the **Volumes** section you can see all persistent volumes used by the stack. These volumes are declared in `compose.yml` and are created automatically by `docker compose up`.

![Figure 11](images/img11.png)

You can also list volumes from the terminal:

```bash
docker volume ls
```

![Figure 12](images/img12.png)

Where Docker volumes live depends on which Docker path you use.

### If you use Docker Desktop

In this case, the Docker daemon does not run inside Ubuntu itself, but inside the `docker-desktop` infrastructure.

To see this, open a Windows terminal (**right-click the Windows icon → Terminal**) and run:

![Figure 13](images/img13.png)

```bash
wsl -l -v
```

![Figure 14](images/img14.png)

This shows that the machine runs two virtual environments: Ubuntu (where you execute the Docker commands) and `docker-desktop`, which runs the Docker daemon itself.

The persistent volumes live inside the file system of the `docker-desktop` VM.

These volumes can be accessed from the Windows host via the following folder:

```
\\wsl.localhost\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes
```

Open Windows Explorer and paste the above path in the address bar. There you will see all directories used as persistent Docker volumes. Each one contains a `_data` subdirectory; whatever you place there becomes visible inside any container that mounts that volume.

![Figure 15](images/img15.png)

### If you use a native Docker Engine inside WSL

In this case, there is no separate `docker-desktop` virtual machine. The Docker daemon runs inside Ubuntu itself, and the volumes live in the WSL file system, usually under:

```bash
/var/lib/docker/volumes
```

You can inspect them with:

```bash
sudo ls /var/lib/docker/volumes
```

or inspect a specific volume with:

```bash
sudo ls /var/lib/docker/volumes/<volume-name>/_data
```

In the lab, however, we prefer to work with `docker cp` and `docker exec`, so that the steps stay identical across both paths.

**Initializing the HDFS file system:** The first time you create the environment, the one-shot `hdfs-init` service automatically creates the required HDFS directories for file uploads and Spark event logs.

This logic is now part of the Docker Compose stack itself, so:

- the main path no longer requires a manual step after `docker compose up --build -d`
- the initialization is idempotent, so it can safely run again
- `spark-history` starts as a separate service after the HDFS bootstrap is ready

The one-shot script that performs this bootstrap is:

<!-- AUTO-CODE: docker/shared/scripts/hdfs-init.sh -->
``` bash
#!/usr/bin/env bash

set -euo pipefail

MAX_ATTEMPTS="${MAX_ATTEMPTS:-60}"
SLEEP_SECONDS="${SLEEP_SECONDS:-2}"
HDFS_URI="${HDFS_URI:-hdfs://namenode:9000}"
HDFS_BIN="${HDFS_BIN:-/opt/hadoop-3.2.1/bin/hdfs}"

hdfs_cmd() {
  "${HDFS_BIN}" "$@"
}

wait_for_hdfs_rpc() {
  local attempt
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    if hdfs_cmd dfsadmin -fs "${HDFS_URI}" -report >/dev/null 2>&1; then
      echo "HDFS RPC endpoint is responding."
      return 0
    fi
    echo "HDFS RPC attempt ${attempt}/${MAX_ATTEMPTS}: not ready yet"
    sleep "$SLEEP_SECONDS"
  done

  echo "HDFS RPC endpoint did not become ready in time." >&2
  return 1
}

wait_for_safe_mode_to_end() {
  local attempt safe_mode_output
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    safe_mode_output="$(hdfs_cmd dfsadmin -fs "${HDFS_URI}" -safemode get 2>/dev/null || true)"
    echo "safe mode attempt ${attempt}/${MAX_ATTEMPTS}: ${safe_mode_output:-unknown}"
    if ! printf '%s' "$safe_mode_output" | grep -q 'Safe mode is ON'; then
      return 0
    fi
    sleep "$SLEEP_SECONDS"
  done

  echo "HDFS stayed in safe mode for too long." >&2
  return 1
}

echo "Waiting for the HDFS RPC endpoint to respond..."
wait_for_hdfs_rpc

# Ask HDFS to leave safe mode when it is already ready enough to accept admin commands.
# If it has already left safe mode, this is a harmless no-op.
hdfs_cmd dfsadmin -fs "${HDFS_URI}" -safemode leave >/dev/null 2>&1 || true

echo "Waiting for HDFS safe mode to end..."
wait_for_safe_mode_to_end

# -mkdir -p makes the bootstrap idempotent. Re-running it repairs the expected
# lab directories without requiring manual cleanup of the whole stack.
echo "Creating the lab directories in HDFS..."
hdfs_cmd dfs -fs "${HDFS_URI}" -mkdir -p /user/root /user/root/examples /logs

echo "HDFS bootstrap completed."
```
<!-- END AUTO-CODE -->

If you ever want to rerun the same bootstrap manually for recovery or diagnostics, you can still do so from the same directory:

```bash
bash ./init-hdfs.sh
```

The reason we create `/logs` in HDFS is that the History Server does not read logs from the host file system. It reads Spark event logs from the same HDFS used by the jobs.

![Figure 16](images/img16.png)

## Running programs on the cluster

Run the following command to estimate π using a Monte Carlo simulation in Java:

```bash
docker exec spark-master /opt/spark/bin/spark-submit --class org.apache.spark.examples.JavaSparkPi /opt/spark/examples/jars/spark-examples.jar
```

If it executes correctly, you will see output similar to:

```
Pi is roughly 3.14638
```

Run the following for the equivalent Python example:

```bash
docker exec spark-master /opt/spark/bin/spark-submit /opt/spark/examples/src/main/python/pi.py
```

### Running your own Spark program on the cluster

Now that we have an initialized HDFS file system and a working container stack, we can run our own Spark programs. To do so, we need to upload:

- **code files** (for example Python scripts)
- **data files** that will be processed (for example the input text for a word count)

### Uploading code

In the repository-based workflow, the recommended path is `docker cp` from the cloned repo, not manual copy through volume paths. This keeps the steps identical whether you use Docker Desktop or a native Docker Engine inside WSL.

![Figure 17](images/img17.png)

From a WSL terminal, run:

```bash
docker cp ~/bigdata-uth/code/wordcount.py spark-master:/mnt/upload/wordcount.py
```

![Figure 18](images/img18.png)

Now the `spark-master` container sees the file at `/mnt/upload`:

```bash
docker exec spark-master ls /mnt/upload
```

![Figure 24](images/img24.png)

The following command prints the contents of the remote `wordcount.py` file as seen from inside the container:

```bash
docker exec spark-master cat /mnt/upload/wordcount.py
```

The script we use here is now the same shared repository script that can run either locally or on a cluster, depending on the `--base-path` we pass to it:

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

If you change `wordcount.py` in the repository, rerun `docker cp` so the updated version is copied into the container.

The code is copied into `spark-master` because `spark-submit` runs there. The data, however, is not kept in the local file system of `spark-master`; it is uploaded to HDFS so it is available to the whole cluster.

### Uploading data files

The `wordcount.py` script expects a base path that contains an `examples/` subdirectory with the input files. At this point, however, the HDFS file system is empty apart from the directories created earlier.

So we must upload an input data file to HDFS.

This happens in **two stages**:
1. Place the file from your local file system into the local file system of the `namenode` container.
2. Run `hdfs dfs -put` inside the `namenode` container to upload the file from `/mnt/upload` into HDFS.

For this purpose, we again use `docker cp`, this time to copy the reference dataset into `namenode`.

From a WSL terminal, run:

```bash
docker cp ~/bigdata-uth/examples/text.txt namenode:/mnt/upload/text.txt
```

![Figure 19](images/img19.png)

Now the `namenode` container sees `text.txt` inside `/mnt/upload`:

```bash
docker exec namenode ls -lah /mnt/upload
```

![Figure 20](images/img20.png)

Upload the file into HDFS with the following commands. We create `/user/root/examples` first because that is where the script will look when we pass `--base-path hdfs://namenode:9000/user/root`:

```bash
docker exec namenode hdfs dfs -mkdir -p /user/root/examples
docker exec namenode hdfs dfs -put -f /mnt/upload/text.txt /user/root/examples/text.txt
```

At this point:
- the Python file to execute is available on the local file system of `spark-master`
- `text.txt` is stored in HDFS

You are ready to run the Spark program:

```bash
docker exec spark-master /opt/spark/bin/spark-submit /mnt/upload/wordcount.py \
  --base-path hdfs://namenode:9000/user/root
```

In this example:

- the input is read from `hdfs://namenode:9000/user/root/examples/text.txt`
- the output is automatically written to a fresh directory such as `hdfs://namenode:9000/user/root/wordcount_output_<app-id>`
- this lets you rerun the example without manually deleting the previous output each time

At this point the execution flow is:

- the driver starts from `spark-master`
- `spark-master` assigns work to the available workers
- the workers read the input data from `hdfs://namenode:9000`
- the execution also writes event logs into HDFS
- the dedicated `spark-history` service later reads those logs to display the application history

## Optional: Run the same reference scripts on the local cluster

This section is not part of the main first pass of the course. The main learning path remains:

- `03_local-spark-workbook`
- `04_remote-spark-kubernetes`
- `05_cluster-queries-rdd-df-sql`

Use the following only as a second pass, to show that the same reference code can also run on the local Spark + HDFS cluster.

The core idea is:

- the code stays the same
- the data stays the same
- only the execution target and the HDFS base path change

From the repository root `~/bigdata-uth`, upload the reference `code/` directory to `spark-master` and the `examples/` directory to `namenode`:

```bash
docker exec spark-master mkdir -p /mnt/upload/code
docker exec namenode mkdir -p /mnt/upload/examples
docker cp ./code/. spark-master:/mnt/upload/code/
docker cp ./examples/. namenode:/mnt/upload/examples/
docker exec namenode bash -c 'hdfs dfs -rm -r -f /user/root/examples || true; hdfs dfs -mkdir -p /user/root/examples; hdfs dfs -put -f /mnt/upload/examples/* /user/root/examples/'
```

In this local stack:

- the reference `spark-submit` script lives under `/mnt/upload/code/...` on `spark-master`
- the input datasets live under `hdfs://namenode:9000/user/root/examples/...`
- the `--base-path` is `hdfs://namenode:9000/user/root`
- you do not use `/user/$USER`, unlike the remote Kubernetes path

Start with a small portability matrix of 3 scripts:

```bash
docker exec spark-master /opt/spark/bin/spark-submit /mnt/upload/code/wordcount.py \
  --base-path hdfs://namenode:9000/user/root

docker exec spark-master /opt/spark/bin/spark-submit /mnt/upload/code/DFQ1.py \
  --base-path hdfs://namenode:9000/user/root

docker exec spark-master /opt/spark/bin/spark-submit /mnt/upload/code/SQLQ2.py \
  --base-path hdfs://namenode:9000/user/root
```

After the runs, inspect the outputs in the local HDFS:

```bash
docker exec namenode hdfs dfs -ls /user/root
```

If everything works, the repository achieves its main portability goal:

- one shared codebase
- local execution without a cluster
- remote execution on a ready Kubernetes cluster
- and optionally execution on a local Spark + HDFS cluster as well

### Monitoring execution

You can watch the currently running job at:

http://localhost:18080

![Figure 21](images/img21.png)

### History Server

Apache Spark includes a useful service that stores log files from all submitted jobs across the master and worker nodes. In this refactored stack, the **History Server** runs as its own `spark-history` container and is available at:

http://localhost:18081

![Figure 22](images/img22.png)

![Figure 23](images/img23.png)

## Useful Linux commands

| Command | Meaning |
|---|---|
| `ls` | list directory contents |
| `pwd` | print the current directory |
| `cd` | change directory |
| `cp` | copy |
| `mv` | move |
| `cat` | print file contents |
| `echo` | print text to the screen |
| `man <command>` | show the manual page for `<command>` |

## Useful HDFS commands

Create a directory in HDFS:

```bash
docker exec namenode hadoop fs -mkdir -p <path>
```

Delete a directory in HDFS:

```bash
docker exec namenode hdfs dfs -rm -r -f <path>
```

Upload a file with overwrite:

```bash
docker exec namenode hdfs dfs -put -f <local-path> <hdfs-path>
```

## Stopping and cleaning up the infrastructure

### Stopping the infrastructure

The following command stops the infrastructure. Files uploaded to HDFS or saved in the persistent volumes of `namenode` and `spark-master` are **not** deleted and remain available. As with `docker compose up`, you must run it from the directory that contains `compose.yml`.

```bash
docker compose down
```

### Cleaning up the infrastructure

If you want to return to a clean initial state, run:

```bash
docker compose down -v --remove-orphans
```

This command:

- stops and removes the containers of this lab stack
- removes the lab network
- deletes the persistent volumes, so the HDFS data, uploaded files, and execution logs are lost

The next time you run `docker compose up --build -d`, the environment starts fresh and you must repeat the HDFS initialization steps.
