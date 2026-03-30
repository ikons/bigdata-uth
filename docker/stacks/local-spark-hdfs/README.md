# Local Spark + HDFS stack

This stack is the implementation used by the student-facing guide `06_local-cluster-infrastructure-docker`.

Quick start:

```bash
cd ~/bigdata-uth/docker/stacks/local-spark-hdfs
docker compose up --build -d
```

Optional manual rerun of the idempotent HDFS bootstrap:

```bash
bash ./init-hdfs.sh
```
