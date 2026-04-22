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
mkdir -p ~/.spark/conf ~/.hadoop/conf
nano ~/bigdata-env.sh
```

Βάλε μέσα:

<!-- AUTO-CODE: templates/wsl/bigdata-env.sh -->
``` bash
# Shared Spark/Hadoop/Kubernetes environment for the lab WSL setup.
# Default baseline: Spark 3.5.8 + Hadoop client 3.4.1 + Java 11.

export SPARK_HOME="$HOME/spark-3.5.8-bin-hadoop3"
export HADOOP_HOME="$HOME/hadoop-3.4.1"
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export SPARK_CONF_DIR="$HOME/.spark/conf"
export HADOOP_CONF_DIR="$HOME/.hadoop/conf"
export PATH="$HOME/.local/bin:$SPARK_HOME/bin:$HADOOP_HOME/bin:$PATH"
export KUBE_EDITOR=nano
export VDCLOUD_USER="your_vdcloud_username"
export HADOOP_USER_NAME="$VDCLOUD_USER"
```
<!-- END AUTO-CODE -->

> **Σημαντικό:** Αντικαταστήστε το `your_vdcloud_username` με το username που σας απέδωσε το εργαστήριο (αυτό που αναγράφεται στο email σύνδεσης). Το username αυτό μπορεί να διαφέρει από το Linux username του WSL σας και χρησιμοποιείται για HDFS paths και Kubernetes namespaces.

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
kubectl -n YOUR_USERNAME-priv get sa spark
```

## 4. Ρύθμιση του Hadoop client

Κρατήστε το HDFS config σε per-user διαδρομή, χωρίς να πειράζετε τα unpacked binaries.

```bash
mkdir -p ~/.hadoop/conf
nano ~/.hadoop/conf/core-site.xml
```

Βάλε μέσα:

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

Έπειτα έλεγξε:

```bash
hdfs dfs -ls /
hdfs dfs -ls /user/$VDCLOUD_USER
```

## 5. Προσωπικό `spark-defaults.conf`

Η πιο πρακτική λύση για τους φοιτητές είναι η λειτουργία συστοιχίας του Kubernetes να είναι η προεπιλογή του `spark-submit` στο WSL.

Δημιούργησε:

```bash
mkdir -p ~/.spark/conf
nano ~/.spark/conf/spark-defaults.conf
```

και βάλε:

<!-- AUTO-CODE: templates/wsl/spark-defaults.conf -->
``` properties
# Replace YOUR_USERNAME with your lab username before first use.

spark.master                                   k8s://https://source-code-master.cluster.local:6443
spark.submit.deployMode                        cluster
spark.kubernetes.namespace                     YOUR_USERNAME-priv
spark.kubernetes.authenticate.driver.serviceAccountName spark
spark.kubernetes.container.image               apache/spark:3.5.8-scala2.12-java11-python3-ubuntu
spark.executor.instances                       1
spark.kubernetes.submission.waitAppCompletion  false
spark.eventLog.enabled                         true
spark.eventLog.dir                             hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/YOUR_USERNAME/logs
spark.history.fs.logDirectory                  hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/YOUR_USERNAME/logs
```
<!-- END AUTO-CODE -->

Πριν από το πρώτο submit:

- αντικατάστησε το `YOUR_USERNAME`
- βεβαιώσου ότι το `spark.master` συμφωνεί με το kubeconfig
- κράτα το image pinned, όχι σκέτο `apache/spark`

## 6. Πρώτη μεταφόρτωση στο HDFS

Από τη ρίζα του cloned repo:

```bash
cd ~/bigdata-uth
hdfs dfs -rm -r -f /user/$VDCLOUD_USER/examples /user/$VDCLOUD_USER/code /user/$VDCLOUD_USER/logs || true
hdfs dfs -mkdir -p /user/$VDCLOUD_USER/logs /user/$VDCLOUD_USER/examples /user/$VDCLOUD_USER/code
hdfs dfs -put -f examples/* /user/$VDCLOUD_USER/examples/
hdfs dfs -put -f code/*.py /user/$VDCLOUD_USER/code/

hdfs dfs -ls /user/$VDCLOUD_USER/examples
hdfs dfs -ls /user/$VDCLOUD_USER/code
```

Η γραμμή με το cleanup είναι προαιρετική, αλλά χρήσιμη όταν ξανατρέχετε τον οδηγό και θέλετε καθαρούς φακέλους χωρίς παλιά uploads.

## 7. Πρώτο `spark-submit`

Αφού το `spark-defaults.conf` είναι ήδη ρυθμισμένο, το πρώτο submit μένει πολύ απλό:

```bash
spark-submit hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/$VDCLOUD_USER/code/wordcount.py \
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
```

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
test -f "$SPARK_CONF_DIR/spark-defaults.conf" && sed -n '1,80p' "$SPARK_CONF_DIR/spark-defaults.conf"
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


