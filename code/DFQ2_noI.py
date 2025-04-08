from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType

username = "ikons"
spark = SparkSession \
    .builder \
    .appName("DF query 2 execution, no Intermediate Table") \
    .getOrCreate()
sc = spark.sparkContext

# ΕΛΑΧΙΣΤΟΠΟΙΗΣΗ ΕΞΟΔΩΝ ΚΑΤΑΓΡΑΦΗΣ (LOGGING)
sc.setLogLevel("ERROR")

job_id = spark.sparkContext.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/DFQ2_nol_{job_id}"


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

# Ορισμός σχήματος για το DataFrame των τμημάτων
departments_schema = StructType([
    StructField("id", IntegerType()),
    StructField("name", StringType()),
])

# Φόρτωση του DataFrame των τμημάτων
departments_df = spark.read.format('csv') \
    .options(header='false') \
    .schema(departments_schema) \
    .load(f"hdfs://hdfs-namenode:9000/user/{username}/examples/departments.csv")

# Καταχώρηση των DataFrames ως προσωρινοί πίνακες (temporary views)
employees_df.createOrReplaceTempView("employees")
departments_df.createOrReplaceTempView("departments")

# Ερώτημα με εσωτερική συνένωση (inner join) για την εξαγωγή υπαλλήλων του 'Dep A'
inner_join_query = """
    SELECT employees.name, employees.salary
    FROM employees
    INNER JOIN departments ON employees.dep_id == departments.id
    WHERE departments.name == 'Dep A'
    ORDER BY employees.salary DESC
"""

# Εκτέλεση του ερωτήματος
joined_data = spark.sql(inner_join_query)

# Εμφάνιση των αποτελεσμάτων της σύνδεσης (για έλεγχο)
joined_data.show()

# Συγχώνευση των partitions σε ένα και αποθήκευση στο HDFS
joined_data.coalesce(1).write.format("csv").option("header", "false").save(output_dir)
