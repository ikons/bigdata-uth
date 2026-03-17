from pyspark.sql import SparkSession

username = "ikons"
sc = SparkSession \
    .builder \
    .appName("RDD query 3 execution") \
    .getOrCreate() \
    .sparkContext

# MINIMIZE LOG OUTPUT
sc.setLogLevel("ERROR")

# Retrieve the job ID and define the output path
job_id = sc.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/RddQ3_{job_id}"

# =======================
# SCHEMA INFORMATION:
# employees:   "emp_id", "emp_name", "salary", "dep_id"
# departments: "id", "dpt_name"
#
# Column mapping for employees:
#   x[0] = emp_id
#   x[1] = emp_name
#   x[2] = salary
#   x[3] = dep_id
#
# Column mapping for departments:
#   x[0] = id
#   x[1] = dpt_name
# =======================

# Load and parse employee data
employees = sc.textFile(f"hdfs://hdfs-namenode:9000/user/{username}/examples/employees.csv") \
    .map(lambda x: x.split(","))  # → [emp_id, emp_name, salary, dep_id]

# Directly compute yearly income using a lambda function
employees_yearly_income = employees.map(lambda x: [x[1], 14 * int(x[2])])  # → [emp_name, 14*salary]

# Print the final output (for testing/debugging)
for item in employees_yearly_income.coalesce(1).collect():
    print(item)

# Save the final output to HDFS
employees_yearly_income.coalesce(1).saveAsTextFile(output_dir)
