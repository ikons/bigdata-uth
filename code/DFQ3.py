from pyspark.sql import SparkSession
from pyspark.sql.types import StructField, StructType, IntegerType, FloatType, StringType
from pyspark.sql.functions import col, udf

username = "ikons"
spark = SparkSession \
    .builder \
    .appName("DF query 3 execution") \
    .getOrCreate()
sc = spark.sparkContext
# MINIMIZE LOG OUTPUT
sc.setLogLevel("ERROR")

job_id = spark.sparkContext.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/DF3_{job_id}"

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

# Define a function that computes yearly income
def calculate_yearly_income(salary):
    return 14 * salary

# Register the UDF
calculate_yearly_income_udf = udf(calculate_yearly_income, FloatType())

# Compute the result by creating a new column
employees_yearly_income_df = employees_df \
    .withColumn("yearly_income", calculate_yearly_income_udf(col("salary"))) \
    .select("emp_name", "yearly_income")

# Display the result
employees_yearly_income_df.show()

# Save the DataFrame to HDFS
employees_yearly_income_df.coalesce(1).write.format("csv").option("header", "false").save(f"{output_dir}")
