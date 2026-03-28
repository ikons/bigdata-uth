# 🔥 Big Data με Apache Spark, HDFS, Docker & Kubernetes

Αυτό το αποθετήριο περιέχει κώδικα, δεδομένα και οδηγίες για την εκτέλεση εργασιών **Apache Spark** με **RDDs**, **DataFrames** και **Map/Reduce** με χρήση **τοπικής (Docker)** και **κατανεμημένης (Kubernetes)** υποδομής για το μάθημα [Συστήματα Διαχείρισης Μεγάλου Όγκου Δεδομένων](https://dit.uth.gr/wp-content/uploads/2023/10/Perigrama-Systimata-Diaxeirisis-Megalou-Ogkou-Dedomenon-neo.pdf) του [Τμήματος Πληροφορικής και Τηλεπικοινωνιών](http://www.dit.uth.gr) [Πανεπιστημίου Θεσσαλίας](http://www.uth.gr).

---

## 📘 Σειρά Μελέτης / Οδηγοί Εκτέλεσης (Markdown)

- `01` [01_workstation-setup](docs/01_workstation-setup): Προετοιμασία σταθμού εργασίας με WSL 2 και Docker Desktop
- `02` [02_vscode-local-authoring](docs/02_vscode-local-authoring): Προτεινόμενη και δοκιμασμένη ροή τοπικής ανάπτυξης Spark με VS Code
- `02` [02_pycharm-local-authoring](docs/02_pycharm-local-authoring): Εναλλακτική ροή τοπικής ανάπτυξης για όσους προτιμούν PyCharm
- `03` [03_local-spark-workbook](docs/03_local-spark-workbook): Τοπική εξάσκηση με Spark, RDD, DataFrame API και Spark SQL
- `04` [04_remote-spark-kubernetes](docs/04_remote-spark-kubernetes): Απομακρυσμένη εκτέλεση Spark σε έτοιμη συστοιχία Kubernetes από WSL/VPN
- `05` [05_cluster-queries-rdd-df-sql](docs/05_cluster-queries-rdd-df-sql): Τα ίδια ερωτήματα στη συστοιχία με RDD, DataFrame API και Spark SQL
- `06` [06_local-cluster-infrastructure-docker](docs/06_local-cluster-infrastructure-docker): Τοπική συστοιχία Spark + HDFS με Docker Compose

📁 Εναλλακτικά, όλοι οι οδηγοί είναι διαθέσιμοι και στον φάκελο [`odigoi/`](./odigoi) σε μορφή `.docx`.

Οι οδηγοί Word στον φάκελο `odigoi/` παράγονται από τα αρχεία Markdown του `docs/` μέσω Pandoc.
Σε Windows, το `scripts/export-docx.ps1` και το `make -C docs docx` χρησιμοποιούν επίσης το Microsoft Word για να ανανεώσουν αυτόματα τον πίνακα περιεχομένων.

### Σύντομη λειτουργική σύνοψη

- Μετά το `01_workstation-setup`, οι τοπικοί οδηγοί (`02`, `03`) υποστηρίζουν δύο διαδρομές:
  - `Windows / PowerShell`, με clone του repo σε φάκελο των Windows
  - `WSL / Ubuntu`, με clone του repo ως `~/bigdata-uth`
- Οι απομακρυσμένοι οδηγοί (`04`, `05`) εκτελούνται μόνο από WSL.
- Ο οδηγός Docker (`06`) θα μπορούσε θεωρητικά να προσαρμοστεί και σε PowerShell, αλλά στο μάθημα τεκμηριώνεται μόνο η WSL διαδρομή για να μείνει ενιαία η εμπειρία.
- Αν δουλέψατε τοπικά από Windows και θέλετε να συνεχίσετε στους απομακρυσμένους οδηγούς, περάστε πρώτα σε WSL clone του repo και φορτώστε το περιβάλλον Spark του WSL:

```bash
cd ~/bigdata-uth
deactivate 2>/dev/null || true
source ~/bigdata-env.sh
hash -r
command -v spark-submit
```


---

## 📁 Δομή Αποθετηρίου

- `code/`: βασικός κώδικας Spark σε Python
- `code/local/rdd/`: μικρά τοπικά παραδείγματα με RDD
- `code/*.py`: βασικά scripts που μπορούν να τρέξουν τοπικά ή απομακρυσμένα
- `code/SQLQ*.py`: εκδοχές Spark SQL των βασικών ερωτημάτων
- `examples/`: αρχεία CSV και κειμένου για δοκιμές (`employees`, `departments`, `text`)
- `docker/`
  - `01-lab1-spark-hdfs/`: Spark + HDFS setup με Docker Compose
  - `02-lab2-spark-history-server/`: Spark History Server setup με Docker
- `docs/`: 📘 Όλοι οι οδηγοί σε μορφή Markdown
- `templates/`: βασικά snippets ρυθμίσεων για WSL, Spark και Hadoop που εισάγονται αυτόματα στα docs
- `odigoi/`: 🧾 Οδηγοί σε `.docx`

---



## 💻 Τοπική Ανάπτυξη Spark με VS Code

📄 Προτεινόμενος οδηγός βήματος `02`: [`02_vscode-local-authoring`](docs/02_vscode-local-authoring)

- Προτεινόμενη προσέγγιση για τοπική ανάπτυξη και αποσφαλμάτωση
- Υποστηρίζει και `Windows / PowerShell` και `WSL / Ubuntu`
- Χρήση `venv`, εγκατάσταση `pyspark==3.5.8` και `psutil`
- Εκτέλεση και debugging μέσα από το VS Code
- Υποστήριξη Spark UI μέσω `localhost:4040`
- Συνέχεια με τον ενιαίο οδηγό τοπικής εξάσκησης στο [`docs/03_local-spark-workbook`](docs/03_local-spark-workbook)

Στο ίδιο βήμα `02`, αν προτιμάτε άλλο IDE, υπάρχει και ο οδηγός [`02_pycharm-local-authoring`](docs/02_pycharm-local-authoring).

---

## 💻 Τοπική Ανάπτυξη Spark με PyCharm

📄 Εναλλακτικός οδηγός βήματος `02`: [`02_pycharm-local-authoring`](docs/02_pycharm-local-authoring)

- Υποστηρίζει και `Windows / PowerShell` και `WSL / Ubuntu`
- Χρήση `venv`, εγκατάσταση `pyspark==3.5.8` και `psutil`
- Ρύθμιση μεταβλητών περιβάλλοντος στο Run Configuration
- Υποστήριξη Spark UI μέσω `localhost:4040`

---

## 🧱 Προετοιμασία Σταθμού Εργασίας (WSL + Docker Desktop)

📄 Οδηγός: [`docs/01_workstation-setup`](docs/01_workstation-setup/)

- Εγκατάσταση WSL 2 και Ubuntu
- Ρύθμιση Docker Desktop για χρήση WSL backend
- Επιβεβαίωση εγκατάστασης και τεστ με `hello-world`

---

## 🐳 Τοπική Συστοιχία Spark + HDFS με Docker

📄 Οδηγός: [`06_local-cluster-infrastructure-docker`](docs/06_local-cluster-infrastructure-docker)

```bash
cd ~/bigdata-uth/docker/01-lab1-spark-hdfs
docker compose up --build -d
```

- Spark UI: http://localhost:8080  
- HDFS NameNode: http://localhost:9870  
- Προαιρετική διαδρομή φορητότητας με τον ίδιο βασικό κώδικα του repo:
```bash
docker exec spark-master /opt/spark/bin/spark-submit /mnt/upload/code/wordcount.py \
  --base-path hdfs://namenode:9000/user/root
```

---

## ☁️ Απομακρυσμένη Εκτέλεση Spark σε Έτοιμη Συστοιχία Kubernetes

📄 Οδηγός: [`04_remote-spark-kubernetes`](docs/04_remote-spark-kubernetes)

- Εκτελείται μόνο από WSL
- Εκτελεί Spark σε Kubernetes (vdcloud)
- Απαιτεί OpenVPN, WSL 2 Ubuntu και per-user `spark-defaults.conf`
- Προτείνει pinned image `apache/spark:3.5.8-scala2.12-java11-python3-ubuntu`
- Χρησιμοποιεί Hadoop client ίδιου major/minor line με το vdcloud HDFS

### Παράδειγμα `spark-submit`:

```bash
deactivate 2>/dev/null || true
source ~/bigdata-env.sh
hash -r
spark-submit \
    hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/$USER/code/wordcount.py \
    --base-path hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/$USER
```

---

## 🔁 Τα Ίδια Ερωτήματα στη Συστοιχία με RDD, DataFrame API και Spark SQL

📄 Οδηγός: [`05_cluster-queries-rdd-df-sql`](docs/05_cluster-queries-rdd-df-sql)

Σε αυτό το εργαστήριο τα βασικά ερωτήματα `Q1-Q3` υλοποιούνται με `RDD`, `DataFrame API` και `Spark SQL` πάνω στα ίδια σύνολα δεδομένων, ώστε ο φοιτητής να συγκρίνει καθαρά τα τρία στυλ API χωρίς να αλλάζει το πρόβλημα. Η εκτέλεση γίνεται μόνο από WSL, πάνω στο περιβάλλον που ρυθμίστηκε στο `04`.

---

## ⚙️ Προετοιμασία Δεδομένων στο HDFS

```bash
cd ~/bigdata-uth
hadoop fs -rm -r -f /user/$USER/examples /user/$USER/code || true
hadoop fs -mkdir -p /user/$USER/examples /user/$USER/code
hadoop fs -put -f examples/* /user/$USER/examples/
hadoop fs -put -f code/*.py /user/$USER/code/

# Επιβεβαίωση
hadoop fs -ls /user/$USER/examples
hadoop fs -ls /user/$USER/code
```

---

## 🧪 Εκτέλεση Ερωτημάτων Spark

| Ερώτημα       | Περιγραφή                                                  | Υλοποίηση                |
|---------------|------------------------------------------------------------|--------------------------|
| Query 1       | 5 υπάλληλοι με τον χαμηλότερο μισθό                        | RDD / DF / SQL           |
| Query 2       | 3 υψηλόμισθοι υπάλληλοι του `Dep A`                        | RDD / DF / SQL           |
| Query 3       | Ετήσιο εισόδημα υπαλλήλων                                  | RDD / DF / SQL           |
| Extra         | Άθροισμα μισθών ανά τμήμα                                  | DF                       |
| Extra         | Ετήσιο εισόδημα με UDF                                     | DF                       |
| Παράρτημα     | Απλοποιημένο παράδειγμα join με δεδομένα στη μνήμη         | RDD                      |
| Word Count    | Καταμέτρηση λέξεων σε αρχείο κειμένου                      | RDD                      |

📈 Τα παραπάνω ερωτήματα μπορούν να παρακολουθηθούν μέσω του Spark History Server, όπως περιγράφεται στο τέλος του [05_cluster-queries-rdd-df-sql](docs/05_cluster-queries-rdd-df-sql).

### Παράδειγμα εκτέλεσης:

```bash
deactivate 2>/dev/null || true
source ~/bigdata-env.sh
hash -r
spark-submit hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/$USER/code/RddQ1.py \
  --base-path hdfs://hdfs-namenode.default.svc.cluster.local:9000/user/$USER
```

Η παραπάνω μορφή υποθέτει ότι στο WSL έχει ήδη ρυθμιστεί το per-user `spark-defaults.conf` του [04_remote-spark-kubernetes](docs/04_remote-spark-kubernetes).

---


## 👤 Συντελεστής

**ikons**  
📬 Για απορίες: [GitHub Issues](https://github.com/ikons/bigdata-uth/issues)
