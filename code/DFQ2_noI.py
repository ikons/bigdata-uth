from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType

username = "ikons"
spark = SparkSession \
    .builder \
    .appName("DF query 2 execution, no Intermediate Table") \
    .getOrCreate()
sc = spark.sparkContext

# MINIMIZE LOG OUTPUT
sc.setLogLevel("ERROR")

job_id = spark.sparkContext.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/DFQ2_nol_{job_id}"

# Define the schema for the employees DataFrame
employees_schema = StructType([
    StructField("id", IntegerType()),
    StructField("name", StringType()),
    StructField("salary", FloatType()),
    StructField("dep_id", IntegerType()),
])

# Load the employees DataFrame
employees_df = spark.read.format('csv') \
    .options(header='false') \
    .schema(employees_schema) \
    .load(f"hdfs://hdfs-namenode:9000/user/{username}/examples/employees.csv")

# Define the schema for the departments DataFrame
departments_schema = StructType([
    StructField("id", IntegerType()),
    StructField("name", StringType()),
])

# Load the departments DataFrame
departments_df = spark.read.format('csv') \
    .options(header='false') \
    .schema(departments_schema) \
    .load(f"hdfs://hdfs-namenode:9000/user/{username}/examples/departments.csv")

# Register the DataFrames as temporary views
employees_df.createOrReplaceTempView("employees")
departments_df.createOrReplaceTempView("departments")

# Inner join query to extract employees from 'Dep A'
inner_join_query = """
    SELECT employees.name, employees.salary
    FROM employees
    INNER JOIN departments ON employees.dep_id == departments.id
    WHERE departments.name == 'Dep A'
    ORDER BY employees.salary DESC
"""

# Execute the query
joined_data = spark.sql(inner_join_query)

# Display the join result (for verification)
joined_data.show()

# Coalesce partitions into one and save to HDFS
joined_data.coalesce(1).write.format("csv").option("header", "false").save(output_dir)
