# Docker Layout

The `docker/` tree is split into three clear roles:

- `images/`: reusable images for each long-lived service (`spark-master`, `spark-worker`, `spark-history`)
- `shared/`: common Spark and Hadoop configuration plus helper scripts shared by multiple stacks
- `stacks/`: ready-to-run `docker compose` stacks for specific usage scenarios

Current stacks:

- `stacks/local-spark-hdfs/`: full local Spark + HDFS stack with automatic HDFS bootstrap and a dedicated History Server
- `stacks/history-server-lab/`: standalone History Server that reads Spark event logs from the lab HDFS

This split keeps Dockerfiles generic, keeps environment-specific configuration outside the images, and makes each compose stack easier to explain and maintain.
