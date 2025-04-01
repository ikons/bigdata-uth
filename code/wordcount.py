from pyspark.sql import SparkSession
username = "ikons"
sc = SparkSession \
    .builder \
    .appName("wordcount example") \
    .getOrCreate() \
    .sparkContext

# ΕΛΑΧΙΣΤΟΠΟΙΗΣΗ ΕΞΟΔΩΝ ΚΑΤΑΓΡΑΦΗΣ (LOGGING)
sc.setLogLevel("ERROR")

# Λήψη του job ID και καθορισμός διαδρομής εξόδου
job_id = sc.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/wordcount_output_{job_id}"

# Φόρτωση αρχείου κειμένου από το HDFS και υπολογισμός συχνοτήτων λέξεων
wordcount = (
    sc.textFile(f"hdfs://hdfs-namenode:9000/user/{username}/examples/text.txt") \
    .flatMap(lambda x: x.split(" "))                 # Διάσπαση κάθε γραμμής σε λέξεις
    .map(lambda x: (x, 1))                           # Χαρτογράφηση (map) κάθε λέξης σε (λέξη, 1)
    .reduceByKey(lambda x, y: x + y)                 # Άθροιση εμφανίσεων για κάθε λέξη
    .sortBy(lambda x: x[1], ascending=False)         # Ταξινόμηση κατά φθίνουσα συχνότητα
)

# Εμφάνιση των αποτελεσμάτων (για έλεγχο)
for item in wordcount.coalesce(1).collect():
    print(item)

# Συγχώνευση για μείωση των αρχείων εξόδου και αποθήκευση στο HDFS
wordcount.saveAsTextFile(output_dir)

# Παράδειγμα αποτελεσμάτων:
# [('text', 3), ('this', 2), ('is', 2), ('like', 2), ('a', 2),
#  ('file', 2), ('words', 2), (',', 2), ('an', 1), ('of', 1),
#  ('with', 1), ('random', 1), ('example', 1)]
