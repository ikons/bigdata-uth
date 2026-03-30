# Standalone History Server for lab logs

This stack starts only a Spark History Server that reads logs from the lab HDFS.

Use the fully qualified HDFS service name in `.env`, not the short `hdfs-namenode` form, so the stack does not depend on a local DNS search domain.

Typical setup:

```bash
cd ~/bigdata-uth/docker/stacks/history-server-lab
cp .env.example .env
# edit .env and set SPARK_HISTORY_LOG_DIR for your user, for example:
# SPARK_HISTORY_LOG_DIR=hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/YOUR_USERNAME/logs
docker compose up --build -d
```

Recommended smoke test:

```bash
curl http://localhost:18081/api/v1/applications
```

Why this endpoint is useful:

- the landing page is mainly an HTML shell
- application data is easier to verify through the API
- the JSON output lets you confirm the exact Spark app id, name, user, and completion status
