from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType

username = "ikons"
spark = SparkSession \
    .builder \
    .appName("DF query 3 execution") \
    .getOrCreate()
sc = spark.sparkContext
# ΕΛΑΧΙΣΤΟΠΟΙΗΣΗ ΕΞΟΔΩΝ ΚΑΤΑΓΡΑΦΗΣ (LOGGING)
sc.setLogLevel("ERROR")

job_id = spark.sparkContext.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/DF3_{job_id}"

# Ορισμός σχήματος για το DataFrame των υπαλλήλων
employees_schema = StructType([
    StructField("emp_id", IntegerType()),
    StructField("emp_name", StringType()),
    StructField("salary", FloatType()),
    StructField("dep_id", IntegerType()),
])

# Φόρτωση του DataFrame των υπαλλήλων
employees_df = spark.read.format('csv') \
    .options(header='false') \
    .schema(employees_schema) \
    .load(f"hdfs://hdfs-namenode:9000/user/{username}/examples/employees.csv")

# Ορισμός σχήματος για το DataFrame των τμημάτων
departments_schema = StructType([
    StructField("id", IntegerType()),
    StructField("dpt_name", StringType()),
])

# Φόρτωση του DataFrame των τμημάτων
departments_df = spark.read.format('csv') \
    .options(header='false') \
    .schema(departments_schema) \
    .load(f"hdfs://hdfs-namenode:9000/user/{username}/examples/departments.csv")

# Εκτέλεση εσωτερικής σύνδεσης (inner join) μεταξύ των DataFrames υπαλλήλων και τμημάτων
joinedDf = employees_df.join(departments_df, employees_df.dep_id == departments_df.id, "inner")

# Εμφάνιση των συνδεδεμένων δεδομένων (για έλεγχο)
joinedDf.show()

# Ομαδοποίηση κατά αναγνωριστικό τμήματος και υπολογισμός αθροίσματος μισθών
groupedDf = joinedDf.groupBy("dep_id").sum("salary")

# Εμφάνιση των ομαδοποιημένων δεδομένων (για έλεγχο)
groupedDf.show()

# Συγχώνευση των DataFrames σε ένα μόνο partition και αποθήκευσή τους στο HDFS

# Αποθήκευση του DataFrame της σύνδεσης στο HDFS
joinedDf.coalesce(1).write.format("csv").option("header", "false").save(f"{output_dir}_joined")

# Αποθήκευση του ομαδοποιημένου DataFrame στο HDFS
groupedDf.coalesce(1).write.format("csv").option("header", "false").save(f"{output_dir}_grouped")
