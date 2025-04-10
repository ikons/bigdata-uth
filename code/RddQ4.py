from pyspark.sql import SparkSession

# Δημιουργία SparkContext

sc = SparkSession \
    .builder \
    .appName("Join Datasets with RDD") \
    .getOrCreate() \
    .sparkContext

# ΕΛΑΧΙΣΤΟΠΟΙΗΣΗ ΕΞΟΔΩΝ ΚΑΤΑΓΡΑΦΗΣ (LOGGING)
sc.setLogLevel("ERROR")


# --------------------------
# Αρχικά δεδομένα
# --------------------------

# Dataset A: (employee_id, employee_name, department_id)
data_a = [
    (1, "George K", 1),
    (2, "John T", 2),
    (3, "Mary M", 1),
    (4, "Jerry S", 3)
]

# Dataset B: (department_id, department_name)
data_b = [
    (1, "Dep A"),
    (2, "Dep B"),
    (3, "Dep C")
]

# --------------------------
# Δημιουργία RDDs
# --------------------------

rdd_a = sc.parallelize(data_a)
rdd_b = sc.parallelize(data_b)

# --------------------------
# Προετοιμασία για ένωση
# --------------------------

# Δημιουργούμε key-value ζεύγη χρησιμοποιώντας το department_id ως κλειδί
# και προσθέτουμε "ετικέτα" για το dataset (1 για A, 2 για B)

# Από το Dataset A:
# (department_id, (1, (employee_id, employee_name, department_id)))
left = rdd_a.map(lambda x: (x[2], (1, x)))

# Από το Dataset B:
# (department_id, (2, (department_id, department_name)))
right = rdd_b.map(lambda x: (x[0], (2, x)))

# --------------------------
# Ένωση των δύο RDDs
# --------------------------

# Κάνουμε union για να βρεθούν όλες οι εγγραφές στο ίδιο RDD
unioned_data = left.union(right)

# --------------------------
# Ομαδοποίηση βάσει του department_id
# --------------------------

# Οι εγγραφές με το ίδιο department_id θα μαζευτούν μαζί
grouped = unioned_data.groupByKey()

# --------------------------
# Συνάρτηση για ενοποίηση των δεδομένων
# --------------------------

def arrange(records):
    left_origin = []   # Εγγραφές από το Dataset A (υπάλληλοι)
    right_origin = []  # Εγγραφές από το Dataset B (τμήματα)
    
    for (source_id, value) in records:
        if source_id == 1:
            left_origin.append(value)
        elif source_id == 2:
            right_origin.append(value)

    # Επιστρέφουμε κάθε συνδυασμό υπαλλήλου με όνομα τμήματος
    return [(employee, dept) for employee in left_origin for dept in right_origin]

# --------------------------
# Τελικό αποτέλεσμα με join
# --------------------------

# Εφαρμόζουμε flatMapValues για να "ξεδιπλώσουμε" τα αποτελέσματα
joined = grouped.flatMapValues(lambda x: arrange(x))

# Επιστρέφει: (department_id, ((employee_id, name, dept_id), (dept_id, dept_name)))
for record in joined.collect():
    print(record)
