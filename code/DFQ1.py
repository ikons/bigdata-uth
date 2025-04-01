from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType
from pyspark.sql.functions import col

username = "ikons"
spark = SparkSession \
    .builder \
    .appName("DF query 1 execution") \
    .getOrCreate()
sc = spark.sparkContext

# ΕΛΑΧΙΣΤΟΠΟΙΗΣΗ ΕΞΟΔΩΝ ΚΑΤΑΓΡΑΦΗΣ (LOGGING)
sc.setLogLevel("ERROR")

job_id = spark.sparkContext.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/DFQ1_{job_id}"

# Ορισμός σχήματος για το DataFrame των υπαλλήλων
employees_schema = StructType([
    StructField("id", IntegerType()),
    StructField("name", StringType()),
    StructField("salary", FloatType()),
    StructField("dep_id", IntegerType()),
])

# Φόρτωση του DataFrame των υπαλλήλων
employees_df = spark.read.format('csv') \
    .options(header='false') \
    .schema(employees_schema) \
    .load(f"hdfs://hdfs-namenode:9000/user/{username}/examples/employees.csv")

# Ταξινόμηση των υπαλλήλων βάσει μισθού
sorted_employees_df = employees_df.sort(col("salary"))

# Εμφάνιση των ταξινομημένων υπαλλήλων (για δοκιμαστικούς σκοπούς)
sorted_employees_df.show(5)

# Συγχώνευση των partitions σε ένα και αποθήκευση στο HDFS
sorted_employees_df.coalesce(1).write.format("csv").option("header", "false").save(output_dir)
