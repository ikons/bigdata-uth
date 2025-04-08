from pyspark.sql import SparkSession

username = "ikons"
sc = SparkSession \
    .builder \
    .appName("RDD query 3 execution") \
    .getOrCreate() \
    .sparkContext

# ΕΛΑΧΙΣΤΟΠΟΙΗΣΗ ΕΞΟΔΩΝ ΚΑΤΑΓΡΑΦΗΣ (LOGGING)
sc.setLogLevel("ERROR")

# Λήψη του job ID και καθορισμός της διαδρομής εξόδου
job_id = sc.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/RddQ3_{job_id}"

# =======================
# ΠΛΗΡΟΦΟΡΙΕΣ ΣΧΗΜΑΤΟΣ:
# employees:   "emp_id", "emp_name", "salary", "dep_id"
# departments: "id", "dpt_name"
#
# Αντιστοίχιση θέσεων για employees:
#   x[0] = emp_id
#   x[1] = emp_name
#   x[2] = salary
#   x[3] = dep_id
#
# Αντιστοίχιση θέσεων για departments:
#   x[0] = id
#   x[1] = dpt_name
# =======================

# Φόρτωση και ανάλυση των δεδομένων υπαλλήλων
employees = sc.textFile(f"hdfs://hdfs-namenode:9000/user/{username}/examples/employees.csv") \
    .map(lambda x: x.split(","))  # → [emp_id, emp_name, salary, dep_id]

# Κατευθείαν υπολογισμός των ετήσιων εισοδημάτων χρησιμοποιώντας lambda function:
employees_yearly_income = employees.map(lambda x: [x[1], 14*(int(x[2]))]) # → [emp_name, 14*salary]

# Εμφάνιση της τελικής εξόδου (για δοκιμή/debugging)
for item in employees_yearly_income.coalesce(1).collect():
    print(item)

# Αποθήκευση της τελικής εξόδου στο HDFS
employees_yearly_income.coalesce(1).saveAsTextFile(output_dir)
