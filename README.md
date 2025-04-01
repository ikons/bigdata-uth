# 🔥 Big Data με Apache Spark, HDFS, Docker & Kubernetes

Αυτό το αποθετήριο περιέχει κώδικα, δεδομένα και οδηγίες για την εκτέλεση εργασιών **Apache Spark** με **RDDs**, **DataFrames** και **Map/Reduce** με χρήση **τοπικής (Docker)** και **κατανεμημένης (Kubernetes)** υποδομής.

---

## 📘 Σειρά Μελέτης / Εκτέλεσης Οδηγιών

1. [`0_Preparatory_lab_Docker_Desktop-wsl.pdf`](./odigoi/0_Preparatory_lab_Docker_Desktop-wsl.pdf): Προετοιμασία περιβάλλοντος (WSL + Docker Desktop)
2. [`0_pycharm_spark_implementation.docx`](./odigoi/0_pycharm_spark_implementation.docx): Εκτέλεση Spark τοπικά με PyCharm
3. [`01_lab1-docker.docx`](./odigoi/01_lab1-docker.docx): Εκκίνηση Spark + HDFS μέσω Docker Compose
4. [`01_lab1-k8s.docx`](./odigoi/01_lab1-k8s.docx): Εκτέλεση Spark Jobs σε Kubernetes (vdcloud)
5. [`02_lab2.docx`](./odigoi/02_lab2.docx): Εκτέλεση ερωτημάτων συνένωσης με χρήση RDD και DataFrames

---

## 📁 Δομή Αποθετηρίου

- `code/`: Κώδικας Spark σε Python (RDD & DataFrame)
- `examples/`: CSV αρχεία για δοκιμές (employees, departments, text)
- `docker/`
  - `01-lab1-spark-hdfs/`: Spark + HDFS setup με Docker Compose
  - `02-lab2-spark-history-server/`: Spark History Server setup με Docker
- `odigoi/`: Όλοι οι οδηγοί σε μορφή `.docx` ή `.pdf`
- `README.md`: Οδηγίες χρήσης και εκτέλεσης

---



## 💻 Εκτέλεση με PyCharm (Τοπική Ανάπτυξη)

📄 Οδηγός: [`0_pycharm_spark_implementation.docx`](./odigoi/0_pycharm_spark_implementation.docx)

- Χρήση `venv`, εγκατάσταση `pyspark` & `psutil`
- Ρύθμιση μεταβλητών περιβάλλοντος στο Run Configuration
- Υποστήριξη Spark UI μέσω `localhost:4040`

---

## 🧱 Προετοιμασία Περιβάλλοντος (WSL + Docker Desktop)

📄 Οδηγός: [`0_Preparatory_lab_Docker_Desktop-wsl.pdf`](./odigoi/0_Preparatory_lab_Docker_Desktop-wsl.pdf)

- Εγκατάσταση WSL 2 και Ubuntu
- Ρύθμιση Docker Desktop για χρήση WSL backend
- Επιβεβαίωση εγκατάστασης και τεστ με `hello-world`

---

## 🐳 Lab 01a: Εκτέλεση Spark + HDFS μέσω Docker

📄 Οδηγός: [`01_lab1-docker.docx`](./odigoi/01_lab1-docker.docx)

```bash
cd docker/01-lab1-spark-hdfs
docker compose up -d
```

- Spark UI: http://localhost:8080  
- HDFS NameNode: http://localhost:9870  
- Εκτέλεση παραδείγματος:
```bash
docker exec spark-master spark-submit /mnt/upload/wordcount.py
```

📂 Ανέβασμα αρχείων:  
```
\wsl.localhost\docker-desktop\mnt\... (shared volume path)
```

---

## ☁️ Lab 01b: Spark σε Kubernetes

📄 Οδηγός: [`01_lab1-k8s.docx`](./odigoi/01_lab1-k8s.docx)

- Εκτελεί Spark σε Kubernetes (vdcloud)
- Απαιτεί OpenVPN & χρήση `k9s` για παρακολούθηση

### Παράδειγμα `spark-submit`:

```bash
spark-submit   --master k8s://https://<k8s-cluster-endpoint>   --deploy-mode cluster   --conf spark.kubernetes.container.image=<spark-image>   hdfs://.../wordcount_localdir.py
```

---

## 🔁 Lab 02: Εκτέλεση ερωτημάτων συνένωσης με την χρήση RDD και DataFrames

📄 Οδηγός: [`02_lab2.docx`](./odigoi/02_lab2.docx)

Σε αυτό το εργαστήριο υλοποιούνται ερωτήματα συνένωσης πινάκων (joins) τόσο με RDDs όσο και με DataFrames. Περιλαμβάνει την ταξινόμηση και την ομαδοποίηση αποτελεσμάτων, καθώς και χρήση SQL queries.

Στο τέλος του οδηγού, γίνεται και σύντομη αναφορά στην ενεργοποίηση και χρήση του **Spark History Server** για την παρακολούθηση των ερωτημάτων μέσω web UI.

---

## ⚙️ Προετοιμασία Δεδομένων στο HDFS

```bash
# Αντιγραφή των φακέλων στο HDFS
hadoop fs -put examples examples
hadoop fs -put code code

# Επιβεβαίωση
hadoop fs -ls examples
hadoop fs -ls code
```

---

## 🧪 Εκτέλεση Ερωτημάτων Spark

| Ερώτημα       | Περιγραφή                                  | Υλοποίηση |
|---------------|---------------------------------------------|------------|
| Query 1       | 5 υπάλληλοι με τον χαμηλότερο μισθό         | RDD / DF   |
| Query 2       | 3 υψηλόμισθοι υπάλληλοι του "Dep A"         | RDD / DF   |
| Query 3       | Άθροισμα μισθών ανά τμήμα                   | DF         |
| Word Count    | Καταμέτρηση λέξεων σε αρχείο κειμένου       | RDD        |

📈 Τα παραπάνω queries μπορούν να παρακολουθηθούν μέσω του Spark History Server (αναφορά στο τέλος του Lab 02).

### Παράδειγμα εκτέλεσης:

```bash
spark-submit hdfs://hdfs-namenode:9000/user/<user>/code/RddQ1.py
```

---




## 📄 Αρχεία Οδηγιών

- [0_Preparatory_lab_Docker_Desktop-wsl.pdf](./odigoi/0_Preparatory_lab_Docker_Desktop-wsl.pdf)
- [0_pycharm_spark_implementation.docx](./odigoi/0_pycharm_spark_implementation.docx)
- [01_lab1-docker.docx](./odigoi/01_lab1-docker.docx)
- [01_lab1-k8s.docx](./odigoi/01_lab1-k8s.docx)
- [02_lab2.docx](./odigoi/02_lab2.docx)

---

## 👤 Συντελεστής

**ikons**  
📬 Για απορίες: [GitHub Issues](https://github.com/ikons/bigdata/issues)
