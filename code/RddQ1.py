from pyspark.sql import SparkSession

username = "ikons"
sc = SparkSession \
    .builder \
    .appName("RDD query 1 execution") \
    .getOrCreate() \
    .sparkContext

# ΕΛΑΧΙΣΤΟΠΟΙΗΣΗ ΕΞΟΔΩΝ ΚΑΤΑΓΡΑΦΗΣ (LOGGING)
sc.setLogLevel("ERROR")

# Λήψη του job ID και καθορισμός της διαδρομής εξόδου
job_id = sc.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/RddQ1_{job_id}"

# Φόρτωση και επεξεργασία δεδομένων
# Στήλες CSV: "id", "name", "salary", "dep_id"
employees = sc.textFile(f"hdfs://hdfs-namenode:9000/user/{username}/examples/employees.csv") \
    .map(lambda x: x.split(","))  # Διαχωρισμός κάθε γραμμής σε λίστα

# Αντιστοίχιση κάθε υπαλλήλου στη μορφή (salary, [id, name, dep_id]) και ταξινόμηση κατά μισθό (αύξουσα σειρά)
# Αντιστοίχιση στηλών:
#   x[0] = id
#   x[1] = name
#   x[2] = salary
#   x[3] = dep_id
sorted_employees = employees.map(lambda x: [int(x[2]), [x[0], x[1], x[3]]]) \
    .sortByKey()

# Εμφάνιση των δεδομένων (για έλεγχο)
for item in sorted_employees.coalesce(1).collect():
    print(item)  # Παράδειγμα εξόδου: [60000, ['123', 'Alice', '5']]

# Συγχώνευση για μείωση αριθμού αρχείων εξόδου και αποθήκευση στο HDFS
sorted_employees.coalesce(1).saveAsTextFile(output_dir)
