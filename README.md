# 🔥 Big Data με Apache Spark, HDFS, Docker & Kubernetes

Αυτό το αποθετήριο περιέχει κώδικα, δεδομένα και πλήρεις οδηγίες για την εκτέλεση εργασιών **Apache Spark** με **RDDs**, **DataFrames**, **Map/Reduce** και **Word Count**, χρησιμοποιώντας υποδομή **τοπική (Docker)** ή **κατανεμημένη (Kubernetes)**, με υποστήριξη **HDFS** και **Spark History Server**.

---

## 📁 Δομή Αποθετηρίου

- `code/`: Κώδικας Spark σε Python (RDD & DataFrame)
- `examples/`: Αρχεία CSV για δοκιμές (employees, departments, text)
- `docker/`
  - `01-lab1-spark-hdfs/`: Spark + HDFS setup με Docker Compose
  - `02-lab2-spark-history-server/`: Spark History Server setup με Docker
- `README.md`: Οδηγίες χρήσης και εκτέλεσης

---

## 🧪 Εκτέλεση Ερωτημάτων Spark

Μπορείτε να εκτελέσετε τις παρακάτω εργασίες με `spark-submit` από το HDFS:

| Ερώτημα       | Περιγραφή                                  | Υλοποίηση |
|---------------|---------------------------------------------|------------|
| Query 1       | 5 υπάλληλοι με τον χαμηλότερο μισθό         | RDD / DF   |
| Query 2       | 3 υψηλόμισθοι υπάλληλοι του "Dep A"         | RDD / DF   |
| Query 3       | Άθροισμα μισθών ανά τμήμα                   | DF         |
| Word Count    | Καταμέτρηση λέξεων σε αρχείο κειμένου       | RDD        |

### Παράδειγμα εκτέλεσης:

```bash
spark-submit hdfs://hdfs-namenode:9000/user/<user>/code/RddQ1.py
```

---

## ⚙️ Προετοιμασία Δεδομένων (HDFS)

```bash
git clone https://github.com/ikons/bigdata.git
cd bigdata

# Ανέβασμα παραδειγμάτων
hadoop fs -put examples examples

# Ανέβασμα κώδικα
hadoop fs -put code code
```

---

## 🐳 Lab 01: Εκτέλεση Spark + HDFS μέσω Docker

Οδηγίες: [`01_lab1-docker.docx`](./01_lab1-docker.docx)

```bash
cd docker/01-lab1-spark-hdfs
docker compose up -d
```

- Spark UI: http://localhost:8080  
- HDFS NameNode: http://localhost:9870  

#### Εκτέλεση παραδείγματος:

```bash
docker exec spark-master spark-submit /mnt/upload/wordcount.py
```

📁 Ανέβασμα αρχείων:  
```
\wsl.localhost\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes\01-lab1-spark-hdfs_spark-master-upload\_data
```

---

## ☁️ Lab 01 (εναλλακτικά): Εκτέλεση Spark σε Kubernetes

Οδηγίες: [`01_lab1-k8s.docx`](./01_lab1-k8s.docx)

- Εκτελεί Spark σε περιβάλλον Kubernetes (vdcloud)
- Απαιτεί σύνδεση μέσω VPN και χρήση `k9s` για παρακολούθηση jobs

### Παράδειγμα εκτέλεσης:

```bash
spark-submit   --master k8s://https://<k8s-cluster-endpoint>   --deploy-mode cluster   --conf spark.kubernetes.container.image=<spark-image>   hdfs://.../wordcount_localdir.py
```

---

## 📈 Lab 02: Spark History Server

Οδηγίες: [`02_lab2.docx`](./02_lab2.docx)

- Καταγραφή ιστορικού Spark jobs
- Προβολή μέσω web UI: http://localhost:18081
- Απαραίτητο: ενεργοποίηση logging στον κώδικα

```python
conf.set("spark.eventLog.enabled", "true")
conf.set("spark.eventLog.dir", "hdfs://...")
```

---

## 📝 Συμβουλή για logs

Για λιγότερη έξοδο στην κονσόλα, προσθέστε:

```python
spark.sparkContext.setLogLevel("ERROR")
```

---

## 📄 Αρχεία Οδηγιών

- [01_lab1-docker.docx](./01_lab1-docker.docx)
- [01_lab1-k8s.docx](./01_lab1-k8s.docx)
- [02_lab2.docx](./02_lab2.docx)

---

## 👤 Συντελεστής

**ikons**  
Για απορίες ή συνεισφορά, χρησιμοποίησε τα [GitHub Issues](https://github.com/ikons/bigdata/issues)
