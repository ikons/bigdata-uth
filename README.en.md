# 🔥 Big Data with Apache Spark, HDFS, Docker & Kubernetes

This repository contains code, datasets, and execution guides for **Apache Spark** workloads using **RDDs**, **DataFrames**, and **Map/Reduce**, both on a **local Docker-based setup** and on a **distributed Kubernetes environment**, for the course [Big Data Management Systems](https://dit.uth.gr/wp-content/uploads/2023/10/Perigrama-Systimata-Diaxeirisis-Megalou-Ogkou-Dedomenon-neo.pdf) of the [Department of Informatics and Telecommunications](http://www.dit.uth.gr), [University of Thessaly](http://www.uth.gr).

---

## 📘 Recommended Study / Execution Order (Markdown)

- `01` [01_workstation-setup](docs/01_workstation-setup): Workstation setup with WSL 2 and Docker
- `02` [02_vscode-local-authoring](docs/02_vscode-local-authoring): Recommended and tested workflow for local Spark development with VS Code
- `02` [02_pycharm-local-authoring](docs/02_pycharm-local-authoring): Alternative local development workflow for students who prefer PyCharm
- `03` [03_local-spark-workbook](docs/03_local-spark-workbook): Local Spark practice with RDD, the DataFrame API, and Spark SQL
- `04` [04_remote-spark-kubernetes](docs/04_remote-spark-kubernetes): Remote Spark execution on a ready Kubernetes cluster from WSL/VPN
- `05` [05_cluster-queries-rdd-df-sql](docs/05_cluster-queries-rdd-df-sql): The same queries on the cluster with RDD, the DataFrame API, and Spark SQL
- `06` [06_local-cluster-infrastructure-docker](docs/06_local-cluster-infrastructure-docker): Local Spark + HDFS cluster with Docker Compose

📁 The same guides are also available under [`odigoi/`](./odigoi) in `.docx` format.

The Word guides under `odigoi/` are generated from the Markdown files in `docs/` with Pandoc.
On Windows, `scripts/export-docx.ps1` and `make -C docs docx` also use Microsoft Word to refresh the table of contents after export.

### Quick operating summary

- After `01_workstation-setup`, the local guides (`02`, `03`) support two paths:
  - `Windows / PowerShell`, with a clone in a Windows folder
  - `WSL / Ubuntu`, with a clone such as `~/bigdata-uth`
- The remote guides (`04`, `05`) run only from WSL.
- The Docker guide (`06`) could theoretically be adapted to PowerShell as well, but the course documents only the WSL path so that the workflow stays consistent.
- If you start locally on Windows and later want to continue to the remote guides, first switch to a WSL clone of the repo and load the WSL Spark environment:

```bash
cd ~/bigdata-uth
deactivate 2>/dev/null || true
source ~/bigdata-env.sh
hash -r
command -v spark-submit
```

---

## 📁 Repository Structure

- `code/`: core Spark code in Python
- `examples/`: Sample CSV/text files (`employees`, `departments`, `text`)
- `docker/`
  - `01-lab1-spark-hdfs/`: Spark + HDFS setup with Docker Compose
  - `02-lab2-spark-history-server/`: Spark History Server setup with Docker
- `docs/`: 📘 All guides in Markdown format
- `templates/`: core WSL, Spark, and Hadoop configuration snippets automatically inserted into the docs
- `odigoi/`: 🧾 Guides in `.docx`

---

## 💻 Local Spark Development with VS Code

📄 Recommended step `02` guide: [`02_vscode-local-authoring`](docs/02_vscode-local-authoring)

- Recommended approach for local development and debugging
- Supports both `Windows / PowerShell` and `WSL / Ubuntu`
- Use `venv`, install `pyspark==3.5.8` and `psutil`
- Run and debug directly from VS Code
- Access the Spark UI at `localhost:4040`

In the same step `02`, if you prefer another IDE, the repository also includes the [`02_pycharm-local-authoring`](docs/02_pycharm-local-authoring) guide.

---

## 💻 Local Spark Development with PyCharm

📄 Alternative step `02` guide: [`02_pycharm-local-authoring`](docs/02_pycharm-local-authoring)

- Supports both `Windows / PowerShell` and `WSL / Ubuntu`
- Use `venv`, install `pyspark==3.5.8` and `psutil`
- Configure the required environment variables in the Run Configuration
- Access the Spark UI at `localhost:4040`

---

## 🧱 Workstation Setup (WSL + Docker)

📄 Guide: [`01_workstation-setup`](docs/01_workstation-setup)

- Install WSL 2 and Ubuntu
- Recommended Docker Desktop setup with the WSL backend
- Optional advanced alternative with a native Docker Engine inside WSL
- Verify the installation with `hello-world`

---

## 🐳 Local Spark + HDFS Cluster with Docker

📄 Guide: [`06_local-cluster-infrastructure-docker`](docs/06_local-cluster-infrastructure-docker)

This lab sets up a local multi-container environment that includes:
- an HDFS cluster with one NameNode and three DataNodes
- a Spark cluster with one Master and four Workers
- persistent Docker volumes for uploaded code and data

Example command:

```bash
cd ~/bigdata-uth/docker/01-lab1-spark-hdfs
docker compose up --build -d
```

Optional portability path with the same core code from the repo:

```bash
docker exec spark-master /opt/spark/bin/spark-submit /mnt/upload/code/wordcount.py \
  --base-path hdfs://namenode:9000/user/root
```

---

## ☁️ Remote Spark Execution on a Ready Kubernetes Cluster

📄 Guide: [`04_remote-spark-kubernetes`](docs/04_remote-spark-kubernetes)

- Runs only from WSL
- Connects to the lab infrastructure through OpenVPN
- Uses WSL 2 Ubuntu, `kubectl`, and `k9s` to manage and monitor execution
- Uses per-user `spark-defaults.conf` with the pinned image `apache/spark:3.5.8-scala2.12-java11-python3-ubuntu`
- Runs Spark jobs on the Kubernetes cluster while reading and writing data from HDFS

Example `spark-submit`:

```bash
deactivate 2>/dev/null || true
source ~/bigdata-env.sh
hash -r
spark-submit \
    hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/$USER/code/wordcount.py \
    --base-path hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/$USER
```

---

## 🔁 The Same Queries on the Cluster with RDD, the DataFrame API, and Spark SQL

📄 Guide: [`05_cluster-queries-rdd-df-sql`](docs/05_cluster-queries-rdd-df-sql)

This lab implements the core `Q1-Q3` relational-style tasks with `RDD`, the `DataFrame API`, and `Spark SQL` on the same datasets, so that students compare API styles without changing the problem at the same time. It runs only from WSL, on top of the environment configured in `04`.

---

## ⚙️ Preparing Data in HDFS

```bash
cd ~/bigdata-uth
hadoop fs -rm -r -f /user/$USER/examples /user/$USER/code || true
hadoop fs -mkdir -p /user/$USER/examples /user/$USER/code
hadoop fs -put -f examples/* /user/$USER/examples/
hadoop fs -put -f code/*.py /user/$USER/code/

# Verify
hadoop fs -ls /user/$USER/examples
hadoop fs -ls /user/$USER/code
```

---

## 🧪 Running Spark Queries

| Query       | Description                                                      | Implementation |
|------------|------------------------------------------------------------------|----------------|
| Query 1    | 5 employees with the lowest salary                               | RDD / DF / SQL |
| Query 2    | 3 highest-paid employees in `Dep A`                              | RDD / DF / SQL |
| Query 3    | Yearly income of all employees                                   | RDD / DF / SQL |
| Extra      | Salary sum per department                                        | DF             |
| Extra      | Yearly income with UDF                                           | DF             |
| Appendix   | Toy join example on in-memory data                               | RDD            |
| Word Count | Count word occurrences in a text file                            | RDD            |

📈 The above queries can be inspected through the Spark History Server (see the end of [05_cluster-queries-rdd-df-sql](docs/05_cluster-queries-rdd-df-sql)).

Example:

```bash
deactivate 2>/dev/null || true
source ~/bigdata-env.sh
hash -r
spark-submit hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/$USER/code/RddQ1.py \
  --base-path hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/$USER
```

This form assumes that your WSL already uses the per-user `spark-defaults.conf` from [04_remote-spark-kubernetes](docs/04_remote-spark-kubernetes).

---

## 👤 Maintainer

**Ioannis Konstantinou**

📬 Questions / issues: [GitHub Issues](https://github.com/ikons/bigdata-uth/issues)
