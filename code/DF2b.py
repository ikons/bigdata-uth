from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType

username = "ikons"
spark = SparkSession \
    .builder \
    .appName("DF query 2b execution") \
    .getOrCreate()
sc = spark.sparkContext
# MINIMIZE LOG OUTPUT
sc.setLogLevel("ERROR")

job_id = spark.sparkContext.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/DF2b_{job_id}"

# Define the schema for the employees DataFrame
employees_schema = StructType([
    StructField("emp_id", IntegerType()),
    StructField("emp_name", StringType()),
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
    StructField("dpt_name", StringType()),
])

# Load the departments DataFrame
departments_df = spark.read.format('csv') \
    .options(header='false') \
    .schema(departments_schema) \
    .load(f"hdfs://hdfs-namenode:9000/user/{username}/examples/departments.csv")

# Execute an inner join between the employee and department DataFrames
joinedDf = employees_df.join(departments_df, employees_df.dep_id == departments_df.id, "inner")

# Display the joined data (for verification)
joinedDf.show()

# Group by department id and compute the salary sum
groupedDf = joinedDf.groupBy("dep_id").sum("salary")

# Display the grouped data (for verification)
groupedDf.show()

# Coalesce both DataFrames into a single partition and save them to HDFS

# Save the joined DataFrame to HDFS
joinedDf.coalesce(1).write.format("csv").option("header", "false").save(f"{output_dir}_joined")

# Save the grouped DataFrame to HDFS
groupedDf.coalesce(1).write.format("csv").option("header", "false").save(f"{output_dir}_grouped")
