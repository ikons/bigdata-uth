# Standalone History Server for lab logs

This stack starts only a Spark History Server that reads logs from the lab HDFS.

Use the fully qualified HDFS service name in `.env`, not the short `hdfs-namenode` form, so the stack does not depend on a local DNS search domain.

Typical setup:

```bash
cd ~/bigdata-uth/docker/stacks/history-server-lab
source ~/bigdata-env.sh
bigdata_write_history_env
cat .env
docker compose up --build -d
```

The `HADOOP_USER_NAME` line is required because the lab HDFS uses simple
authentication and student log directories are private. Without it the History
Server container runs as the Linux user `root`, which is not the intended HDFS
identity for reading your event logs.

Recommended smoke test:

```bash
curl http://localhost:18081/api/v1/applications
```

Why this endpoint is useful:

- the landing page is mainly an HTML shell
- application data is easier to verify through the API
- the JSON output lets you confirm the exact Spark app id, name, user, and completion status
