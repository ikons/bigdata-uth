from pyspark.sql import SparkSession

username = "ikons"
sc = SparkSession \
    .builder \
    .appName("RDD query 2 execution") \
    .getOrCreate() \
    .sparkContext

# ΕΛΑΧΙΣΤΟΠΟΙΗΣΗ ΕΞΟΔΩΝ ΚΑΤΑΓΡΑΦΗΣ (LOGGING)
sc.setLogLevel("ERROR")

# Λήψη του job ID και καθορισμός της διαδρομής εξόδου
job_id = sc.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/RddQ2_{job_id}"

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
employees = sc.textFile("hdfs://hdfs-namenode:9000/user/ikons/examples/employees.csv") \
    .map(lambda x: x.split(","))  # → [emp_id, emp_name, salary, dep_id]

# Φόρτωση και ανάλυση των δεδομένων τμημάτων
departments = sc.textFile("hdfs://hdfs-namenode:9000/user/ikons/examples/departments.csv") \
    .map(lambda x: x.split(","))  # → [id, dpt_name]

# Φιλτράρισμα μόνο των τμημάτων με dpt_name == "Dep A"
depA = departments.map(lambda x: x if (x[1] == "Dep A") else None) \
    .filter(lambda x: x is not None)

# Μορφοποίηση υπαλλήλων σε (dep_id, [emp_id, emp_name, salary])
# Χρήση του x[3] = dep_id ως κλειδί
employees_formatted = employees.map(lambda x: [x[3], [x[0], x[1], x[2]]])

# Μορφοποίηση τμημάτων σε (id, [dpt_name])
# Χρήση του x[0] = id ως κλειδί
depA_formatted = depA.map(lambda x: [x[0], [x[1]]])

# Συνένωση υπαλλήλων με το τμήμα "Dep A" βάσει dep_id
# Αποτέλεσμα: (dep_id, ([emp_id, emp_name, salary], [dpt_name]))
joined_data = employees_formatted.join(depA_formatted)

# Εξαγωγή μόνο των στοιχείων υπαλλήλων (χωρίς τα στοιχεία του τμήματος)
# Αποτέλεσμα: [emp_id, emp_name, salary]
get_employees = joined_data.map(lambda x: x[1][0])

# Ταξινόμηση υπαλλήλων κατά φθίνουσα σειρά μισθού
# Είσοδος: [emp_id, emp_name, salary] — x[2] = salary
# Έξοδος: (salary, [emp_id, emp_name])
sorted_employees = get_employees.map(lambda x: [int(x[2]), [x[0], x[1]]]) \
    .sortByKey(ascending=False)

# Δημιουργία RDD με διαχωριστική γραμμή για την τελική έξοδο
delimiter = ["=========="]
delimiter_rdd = sc.parallelize(delimiter)  # RDD μίας γραμμής

# Συνένωση όλων των RDD με διαχωριστικά ενδιάμεσα
final_rdd = employees_formatted.union(delimiter_rdd) \
    .union(departments) \
    .union(delimiter_rdd) \
    .union(joined_data) \
    .union(delimiter_rdd) \
    .union(sorted_employees)

# Εμφάνιση της τελικής εξόδου (για δοκιμή/debugging)
for item in final_rdd.coalesce(1).collect():
    print(item)

# Αποθήκευση της τελικής εξόδου στο HDFS
final_rdd.coalesce(1).saveAsTextFile(output_dir)
