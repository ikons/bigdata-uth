from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType
from pyspark.sql.functions import col, udf

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

# Δήλωση συνάρτησης υπολογισμού του ετήσιου εισοδήματος
def calculate_yearly_income(salary):
    return 14*salary

# Καταχώρηση του udf
calculate_yearly_income_udf = udf(calculate_yearly_income, FloatType())

# Υπολογισμός με δημιουργία νέας στήλης
employees_yearly_income_df = employees_df \
    .withColumn("yearly_income", calculate_yearly_income_udf(col("salary"))) \
    .select("emp_name", "yearly_income")

# Εμφάνιση αποτελέσματος
employees_yearly_income_df.show()

# Αποθήκευση του DataFrame στο HDFS
employees_yearly_income_df.coalesce(1).write.format("csv").option("header", "false").save(f"{output_dir}")
