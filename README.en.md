# 🔥 Big Data with Apache Spark, HDFS, Docker & Kubernetes

This repository contains code, datasets, and execution guides for **Apache Spark** workloads using **RDDs**, **DataFrames**, and **Map/Reduce**, both on a **local Docker-based setup** and on a **distributed Kubernetes environment**, for the course [Big Data Management Systems](https://dit.uth.gr/wp-content/uploads/2023/10/Perigrama-Systimata-Diaxeirisis-Megalou-Ogkou-Dedomenon-neo.pdf) of the [Department of Informatics and Telecommunications](http://www.dit.uth.gr), [University of Thessaly](http://www.uth.gr).

---

## 📘 Recommended Study / Execution Order (Markdown)

1. [00_Preparatory-lab](docs/00_Preparatory-lab): Environment preparation (WSL + Docker Desktop)
2. [00_pycharm](docs/00_pycharm): Running Spark locally with PyCharm
3. [01_lab1-docker](docs/01_lab1-docker): Launching Spark + HDFS with Docker Compose
4. [01_lab1-k8s](docs/01_lab1-k8s): Running Spark jobs on Kubernetes (vdcloud)
5. [02_lab2](docs/02_lab2): Join queries with RDDs, DataFrames, and SQL

📁 The same guides are also available under [`odigoi/`](./odigoi) in `.docx` format (and one preparatory guide in `.pdf`).

---

## 📁 Repository Structure

- `code/`: Spark code in Python (RDD & DataFrame examples)
- `examples/`: Sample CSV/text files (`employees`, `departments`, `text`)
- `docker/`
  - `01-lab1-spark-hdfs/`: Spark + HDFS setup with Docker Compose
  - `02-lab2-spark-history-server/`: Spark History Server setup with Docker
- `docs/`: 📘 All guides in Markdown format
- `odigoi/`: 🧾 Guides in `.docx` and `.pdf`

---

## 💻 Running Spark with PyCharm (Local Development)

📄 Guide: [`00_pycharm`](docs/00_pycharm)

- Use `venv`, install `pyspark` and `psutil`
- Configure the required environment variables in the Run Configuration
- Access the Spark UI at `localhost:4040`

---

## 🧱 Environment Preparation (WSL + Docker Desktop)

📄 Guide: [`00_Preparatory-lab`](docs/00_Preparatory-lab)

- Install WSL 2 and Ubuntu
- Configure Docker Desktop to use the WSL backend
- Verify the installation with `hello-world`

---

## 🐳 Lab 01a: Running Spark + HDFS with Docker

📄 Guide: [`01_lab1-docker`](docs/01_lab1-docker)

This lab sets up a local multi-container environment that includes:
- an HDFS cluster with one NameNode and three DataNodes
- a Spark cluster with one Master and three Workers
- persistent Docker volumes for uploaded code and data

Example command:

```bash
cd ~/bigdata-uth/docker/01-lab1-spark-hdfs
docker-compose up --build -d
```

Upload example data to HDFS:

```bash
docker exec namenode hdfs dfs -put -f /mnt/upload/text.txt /user/root/text.txt
```

---

## ☁️ Lab 01b: Spark on Kubernetes

📄 Guide: [`01_lab1-k8s`](docs/01_lab1-k8s)

- Connects to the lab infrastructure through OpenVPN
- Uses `kubectl` and `k9s` to manage and monitor execution
- Runs Spark jobs on the Kubernetes cluster while reading/writing data from HDFS

Example `spark-submit`:

```bash
spark-submit \
    --master k8s://https://10.42.0.1:6443 \
    --deploy-mode cluster \
    --name wordcount \
    --conf spark.kubernetes.namespace=testuser-priv \
    --conf spark.executor.instances=5 \
    --conf spark.eventLog.enabled=true \
    --conf spark.eventLog.dir=hdfs://hdfs-namenode:9000/user/testuser/logs \
    hdfs://hdfs-namenode:9000/user/testuser/wordcount_localdir.py
```

---

## 🔁 Lab 02: Join Queries with RDDs, DataFrames, and SQL

📄 Guide: [`02_lab2`](docs/02_lab2)

This lab implements classic relational-style processing tasks in Spark, including:
- sorting and filtering employees
- joins between employees and departments
- yearly income calculation
- an additional example using Spark SQL and the DataFrame API

It also includes setup instructions for the **Spark History Server** to inspect past executions via the web UI.

---

## ⚙️ Preparing Data in HDFS

```bash
# Copy the example data and code into HDFS
hadoop fs -put examples examples
hadoop fs -put code code

# Verify
hadoop fs -ls examples
hadoop fs -ls code
```

---

## 🧪 Running Spark Queries

| Query       | Description                                                      | Implementation |
|------------|------------------------------------------------------------------|----------------|
| Query 1    | 5 employees with the lowest salary                               | RDD / DF       |
| Query 2    | 3 highest-paid employees in "Dep A" / salary sum per department | RDD / DF       |
| Query 3    | Yearly income of all employees                                   | RDD / DF       |
| Query 4    | Join employees with departments using only RDDs                  | RDD            |
| Word Count | Count word occurrences in a text file                            | RDD            |

📈 The above queries can be inspected through the Spark History Server (see the end of [02_lab2](docs/02_lab2)).

Example:

```bash
# ⚠️ Replace ikons with your own username
spark-submit hdfs://hdfs-namenode:9000/user/ikons/code/RddQ1.py
```

---

## 👤 Maintainer

**Ioannis Konstantinou**

📬 Questions / issues: [GitHub Issues](https://github.com/ikons/bigdata-uth/issues)
