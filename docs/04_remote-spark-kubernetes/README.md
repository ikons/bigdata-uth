# Απομακρυσμένη εκτέλεση Spark σε Kubernetes από WSL

Ο οδηγός αυτός ακολουθεί την τοπική ανάπτυξη και προηγείται του οδηγού [ίδιων ερωτημάτων στη συστοιχία](../05_cluster-queries-rdd-df-sql/README.md).

Ο στόχος εδώ δεν είναι να μάθετε νέο Spark API. Ο στόχος είναι να στήσετε μια σταθερή ροή εργασίας στο WSL, όπου:

- η τοπική ανάπτυξη γίνεται σε VS Code ή PyCharm
- η αποστολή των εργασιών γίνεται από το δικό σας WSL μέσω VPN
- η συστοιχία Kubernetes δίνεται ήδη έτοιμη από το εργαστήριο
- το `spark-submit`, το `kubectl` και το `hdfs` δουλεύουν από το ίδιο περιβάλλον

Ο οδηγός αυτός εκτελείται μόνο από WSL. Θεωρητικά θα μπορούσε να στηθεί και διαδρομή απευθείας από τα Windows, αλλά στο μάθημα δεν την τεκμηριώνουμε, γιατί η ροή βασίζεται σε `spark-submit`, `hdfs`, `kubectl`, `~/.kube`, `~/.spark`, `~/.hadoop` και γενικά σε περιβάλλον τερματικού τύπου Linux.

## Προτεινόμενες εκδόσεις

Η προτεινόμενη βάση λογισμικού για το μάθημα είναι:

| Συστατικό | Προτεινόμενη έκδοση |
| --- | --- |
| Java στο WSL | `OpenJDK 11` |
| Spark client στο WSL | `spark-3.5.8-bin-hadoop3` |
| Hadoop client στο WSL | `hadoop-3.4.1` |
| Spark image στο Kubernetes | `apache/spark:3.5.8-scala2.12-java11-python3-ubuntu` |
| HDFS server στο vdcloud | `3.4.1` |

Με άλλα λόγια, η βασική έκδοση λογισμικού του μαθήματος είναι:

- `Spark 3.5.8`
- `Java 11`
- `Hadoop client 3.4.1`
- pinned image `apache/spark:3.5.8-scala2.12-java11-python3-ubuntu`

## Τι χρειάζεστε πριν ξεκινήσετε

- WSL 2 με Ubuntu
- VPN profile του εργαστηρίου
- kubeconfig του εργαστηρίου
- κλωνοποιημένο αποθετήριο `~/bigdata-uth`
- Java, Spark client και Hadoop client μέσα στο WSL
- προσωπικό namespace `<username>-priv`
- service account `spark` μέσα σε αυτό το namespace

Οι οδηγίες εγκατάστασης `OpenVPN`, `kubectl` και του αρχικού `~/.kube/config` βρίσκονται ήδη στον [01_workstation-setup](../01_workstation-setup/README.md). Από εδώ και πέρα υποθέτουμε ότι το VPN είναι ήδη συνδεδεμένο και ότι το `kubectl config current-context` δουλεύει.

## 1. Έλεγχος Java, Spark και Hadoop στο WSL

Οι βασικές εγκαταστάσεις του WSL ανήκουν στον `01_workstation-setup`. Αν είναι η πρώτη φορά που περνάτε αυτόν τον οδηγό, πηγαίνετε πρώτα στο βήμα `2`, δημιουργήστε το κοινό αρχείο `~/bigdata-env.sh` και μετά επιστρέψτε εδώ.

Αν το περιβάλλον έχει ήδη στηθεί, φορτώστε το πρώτα και μετά επιβεβαιώστε ότι βλέπετε τα σωστά binaries:

```bash
. ~/.profile
java -version
command -v spark-submit
command -v hdfs
spark-submit --version
hadoop version
```

Αν κάποιο από τα παραπάνω λείπει, επιστρέψτε πρώτα στον `01_workstation-setup` και ολοκληρώστε την εγκατάσταση του `Spark 3.5.8` και του `Hadoop client 3.4.1`.

## 2. Κοινό αρχείο περιβάλλοντος στο WSL

Κρατήστε τις διαδρομές σε ένα κοινό αρχείο, όχι σκορπισμένες στο `~/.bashrc`.

```bash
cd ~/bigdata-uth
mkdir -p ~/.spark/conf ~/.hadoop/conf
cp templates/wsl/bigdata-env.sh ~/bigdata-env.sh
nano ~/bigdata-env.sh
```

Στο πάνω μέρος του αρχείου άλλαξε μόνο τη γραμμή:

```bash
export VDCLOUD_USER="your_vdcloud_username"
```

και βάλε το username που σου απέδωσε το εργαστήριο, π.χ.:

```bash
export VDCLOUD_USER="ikons"
```

Δεν χρειάζεται να το αντιγράψεις με το χέρι. Για έλεγχο, το αρχείο που αντέγραψες περιέχει:

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

> **Σημαντικό:** Το `VDCLOUD_USER` μπορεί να διαφέρει από το Linux username του WSL σας και χρησιμοποιείται για HDFS paths και Kubernetes namespaces.

### Ενεργοποίηση του περιβάλλοντος σε κάθε νέο shell

Το Bash διαβάζει διαφορετικό αρχείο εκκίνησης ανάλογα με τον τρόπο που ανοίγει ένα shell:

- `~/.profile` — διαβάζεται μία φορά κατά την εκκίνηση ενός **login shell** (κάθε φορά που ανοίγει το WSL). Οι μεταβλητές που ορίζονται εδώ κληρονομούνται από τις θυγατρικές διεργασίες, συμπεριλαμβανομένων αυτών που εκκινεί το `spark-submit`.
- `~/.bashrc` — διαβάζεται σε κάθε νέο **interactive shell** (π.χ. κάθε φορά που ανοίγετε νέα καρτέλα τερματικού).

Για να φορτώνεται αυτόματα το `bigdata-env.sh` και στις δύο περιπτώσεις, εκτελέστε:

```bash
echo '. ~/bigdata-env.sh' >> ~/.profile
echo '. ~/bigdata-env.sh' >> ~/.bashrc
```

Ο τελεστής `>>` **προσθέτει** μία γραμμή στο αρχείο χωρίς να διαγράψει το υπόλοιπο περιεχόμενο. Ο τελεστής `.` είναι συντομογραφία του `source` — εκτελεί το αρχείο μέσα στο τρέχον shell.

> **Εκτελέστε κάθε εντολή ακριβώς μία φορά.** Αν εκτελεστεί ξανά, η γραμμή θα προστεθεί δεύτερη φορά. Αν συμβεί αυτό, ανοίξτε το αρχείο με `nano ~/.profile` ή `nano ~/.bashrc` και διαγράψτε τη διπλή γραμμή.

Εφαρμόστε τις αλλαγές στο τρέχον session χωρίς επανεκκίνηση:

```bash
. ~/.profile
```

και έλεγξε:

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

Το `command -v spark-submit` πρέπει να δείχνει στην εγκατάσταση Spark του WSL, π.χ. `/home/$USER/spark-3.5.8-bin-hadoop3/bin/spark-submit`. Αν δείχνει σε `.venv/bin/spark-submit`, τότε είστε ακόμη στο τοπικό Python περιβάλλον και το submit δεν θα πάει στη συστοιχία Kubernetes όπως περιμένετε.

## 3. kubeconfig, kubectl και DNS

Βάλε το kubeconfig στη θέση:

```bash
mkdir -p ~/.kube
cp /path/to/config ~/.kube/config
```

Μετά έλεγξε:

```bash
kubectl config current-context
kubectl config get-contexts
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}{"\n"}'
```

Το endpoint του Kubernetes API δεν πρέπει να αντιγράφεται από παλιά screenshots. Πρέπει να προκύπτει από το kubeconfig που έδωσε το εργαστήριο.

Στην τρέχουσα εργαστηριακή ρύθμιση, το σωστό internal DNS name είναι `source-code-master.cluster.local`, αλλά το kubeconfig παραμένει η πηγή αλήθειας.

Για τη ροή WSL, ελέγξτε και τη διαθεσιμότητα DNS/HDFS:

```bash
getent hosts source-code-master.cluster.local
getent hosts hdfs-namenode.default.svc.cluster.local
kubectl -n "$VDCLOUD_USER-priv" get sa spark
```

## 4. Ρύθμιση του Hadoop client

Κρατήστε το HDFS config σε per-user διαδρομή, χωρίς να πειράζετε τα unpacked binaries.

```bash
cd ~/bigdata-uth
mkdir -p ~/.hadoop/conf
cp templates/wsl/core-site.xml ~/.hadoop/conf/core-site.xml
cp templates/wsl/log4j.properties ~/.hadoop/conf/log4j.properties
```

Το `core-site.xml` περιέχει:

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

Αν το εργαστήριο δώσει και `hdfs-site.xml`, βάλ' το επίσης στο `~/.hadoop/conf/`.

Το `log4j.properties` είναι μόνο για να μη βγάζει κάθε `hdfs` εντολή το warning `log4j.properties is not found`.

Έπειτα έλεγξε:

```bash
hdfs dfs -ls /
hdfs dfs -ls /user/$VDCLOUD_USER
```

## 5. Προσωπικό `spark-defaults.conf`

Η πιο πρακτική λύση για τους φοιτητές είναι η λειτουργία συστοιχίας του Kubernetes να είναι η προεπιλογή του `spark-submit` στο WSL.

Το `spark-defaults.conf` πρέπει να περιέχει πραγματικές τιμές, όχι shell variables. Δημιούργησέ το από το `VDCLOUD_USER` που έχεις ήδη ορίσει στο `~/bigdata-env.sh`:

```bash
source ~/bigdata-env.sh
bigdata_write_spark_defaults
cat ~/.spark/conf/spark-defaults.conf
```

Το helper function γράφει το παρακάτω template με το δικό σου vdcloud username:

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

Πριν από το πρώτο submit:

- έλεγξε ότι στο αρχείο εμφανίζεται το δικό σου vdcloud username
- βεβαιώσου ότι το `spark.master` συμφωνεί με το kubeconfig
- κράτα το image pinned, όχι σκέτο `apache/spark`
- κράτα τις τρεις ρυθμίσεις `HADOOP_USER_NAME` και `spark.kubernetes.file.upload.path`, γιατί τα HDFS home directories είναι ιδιωτικά

## 6. Έλεγχος προσωπικού HDFS χώρου

Από τη ρίζα του cloned repo:

```bash
cd ~/bigdata-uth
hdfs dfs -ls -d /user/$VDCLOUD_USER
hdfs dfs -ls -d /user/$VDCLOUD_USER/.spark-upload
hdfs dfs -ls -d /user/$VDCLOUD_USER/logs
```

Οι κατάλογοι `/user/$VDCLOUD_USER`, `.spark-upload` και `logs` δημιουργούνται από το εργαστήριο όταν δημιουργείται ο λογαριασμός. Πρέπει να υπάρχουν ήδη και να είναι ιδιωτικοί. Αν λείπει κάποιος από αυτούς, μην αλλάξεις permissions μόνος σου· ενημέρωσε τον διδάσκοντα.

Για τα παραδείγματα του οδηγού, ανέβασε μόνο τα δεδομένα:

```bash
hdfs dfs -mkdir -p /user/$VDCLOUD_USER/examples
hdfs dfs -chmod 700 /user/$VDCLOUD_USER/examples
hdfs dfs -put -f examples/* /user/$VDCLOUD_USER/examples/
hdfs dfs -ls /user/$VDCLOUD_USER/examples
```

Δεν ανεβάζουμε τα `code/*.py` στο HDFS. Τα scripts μένουν τοπικά στο WSL και το Spark τα ανεβάζει προσωρινά στο ιδιωτικό `/user/$VDCLOUD_USER/.spark-upload` όταν τα περνάμε στο `spark-submit`.

## 7. Πρώτο `spark-submit`

Αφού το `spark-defaults.conf` είναι ήδη ρυθμισμένο, το πρώτο submit μένει πολύ απλό:

```bash
spark-submit code/wordcount.py \
  --base-path hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/$VDCLOUD_USER
```

Ο βασικός κώδικας του παραδείγματος είναι:

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

## 8. Παρακολούθηση της εκτέλεσης

Μετά το submit:

```bash
kubectl -n "$VDCLOUD_USER-priv" get pods -o wide
kubectl -n "$VDCLOUD_USER-priv" logs <driver-pod-name>
kubectl -n "$VDCLOUD_USER-priv" describe pod <driver-pod-name>
```

Αν χρησιμοποιείς `k9s`:

```bash
k9s -n "$VDCLOUD_USER-priv"
```

Έπειτα έλεγξε output και event logs:

```bash
hdfs dfs -ls /user/$VDCLOUD_USER | grep wordcount_output
hdfs dfs -ls /user/$VDCLOUD_USER/logs | tail -n 5
hdfs dfs -ls /user/$VDCLOUD_USER/.spark-upload
```

Όταν δεν τρέχει πλέον job του χρήστη, μπορείς να καθαρίσεις τα προσωρινά staged scripts:

```bash
hdfs dfs -rm -r -skipTrash /user/$VDCLOUD_USER/.spark-upload/spark-upload-* 2>/dev/null || true
```

### Τοπικός History Server για τα απομακρυσμένα logs

Αν θέλεις να δεις τα event logs του vdcloud από τοπικό Spark History Server:

```bash
cd ~/bigdata-uth/docker/stacks/history-server-lab
source ~/bigdata-env.sh
bigdata_write_history_env
cat .env
```

Το `.env` πρέπει να περιέχει τις δικές σου τιμές:

```env
SPARK_HISTORY_UI_HOST_PORT=18081
HADOOP_USER_NAME=VDCLOUD_USER
SPARK_HISTORY_LOG_DIR=hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/VDCLOUD_USER/logs
```

Μετά ξεκίνα τον History Server:

```bash
docker compose up --build -d
curl http://localhost:18081/api/v1/applications
```

Το `HADOOP_USER_NAME` είναι απαραίτητο γιατί τα `/user/<username>/logs` είναι ιδιωτικά στο HDFS.

## Αντιμετώπιση προβλημάτων

### Το `spark-submit` δεν βρίσκει τα paths

Συνήθως σημαίνει ότι το `bigdata-env.sh` δεν φορτώθηκε στο shell που χρησιμοποιείς.

Έλεγξε:

```bash
echo "$SPARK_HOME"
echo "$HADOOP_HOME"
command -v spark-submit
command -v hdfs
```

### Το job έτρεξε τοπικά αντί για Kubernetes

Συνήθως σημαίνει ότι λείπει ή δεν φορτώθηκε το `spark-defaults.conf`.

Έλεγξε:

```bash
spark-submit --version
test -f "$SPARK_CONF_DIR/spark-defaults.conf" && cat "$SPARK_CONF_DIR/spark-defaults.conf"
```

### Λείπει το `spark.kubernetes.file.upload.path`

Αν το `spark-submit code/wordcount.py` ζητήσει `spark.kubernetes.file.upload.path`, λείπει η ρύθμιση που λέει στο Spark πού θα ανεβάσει προσωρινά το local script. Τρέξε ξανά:

```bash
source ~/bigdata-env.sh
bigdata_write_spark_defaults
```

### `Permission denied` στο `.spark-upload` ή στα `logs`

Έλεγξε ότι το `~/.spark/conf/spark-defaults.conf` περιέχει το δικό σου username και στις τρεις σχετικές γραμμές:

```properties
spark.kubernetes.driverEnv.HADOOP_USER_NAME VDCLOUD_USER
spark.executorEnv.HADOOP_USER_NAME VDCLOUD_USER
spark.kubernetes.file.upload.path hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/VDCLOUD_USER/.spark-upload
```

### Τα hostnames δεν επιλύονται από το WSL

Έλεγξε πρώτα:

```bash
getent hosts source-code-master.cluster.local
getent hosts hdfs-namenode.default.svc.cluster.local
```

Αν αυτά δεν λύνουν, το πρόβλημα είναι στο VPN ή στην αλυσίδα επίλυσης DNS του WSL, όχι στο Spark script.

## Τι ακολουθεί

Αφού περάσει το πρώτο απομακρυσμένο submit, προχωρήστε στον οδηγό [ίδιων ερωτημάτων στη συστοιχία](../05_cluster-queries-rdd-df-sql/README.md), όπου εκτελούμε τα ίδια `Q1-Q3` ερωτήματα με `RDD`, `DataFrame API` και `Spark SQL`.
