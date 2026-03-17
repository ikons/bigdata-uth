from pyspark.sql import SparkSession

username = "ikons"
sc = SparkSession \
    .builder \
    .appName("RDD query 2 execution") \
    .getOrCreate() \
    .sparkContext

# MINIMIZE LOG OUTPUT
sc.setLogLevel("ERROR")

# Retrieve the job ID and define the output path
job_id = sc.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/RddQ2_{job_id}"

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

# Load and parse department data
departments = sc.textFile(f"hdfs://hdfs-namenode:9000/user/{username}/examples/departments.csv") \
    .map(lambda x: x.split(","))  # → [id, dpt_name]

# Keep only departments with dpt_name == "Dep A"
depA = departments.filter(lambda x: x[1] == "Dep A")

# Format employees as (dep_id, [emp_id, emp_name, salary])
# Use x[3] = dep_id as the key
employees_formatted = employees.map(lambda x: [x[3], [x[0], x[1], x[2]]])

# Format departments as (id, [dpt_name])
# Use x[0] = id as the key
depA_formatted = depA.map(lambda x: [x[0], [x[1]]])

# Join employees with department "Dep A" using dep_id
# Result: (dep_id, ([emp_id, emp_name, salary], [dpt_name]))
joined_data = employees_formatted.join(depA_formatted)

# Extract only employee fields (without department fields)
# Result: [emp_id, emp_name, salary]
get_employees = joined_data.map(lambda x: x[1][0])

# Sort employees by salary in descending order
# Input: [emp_id, emp_name, salary] — x[2] = salary
# Output: (salary, [emp_id, emp_name])
sorted_employees = get_employees.map(lambda x: [int(x[2]), [x[0], x[1]]]) \
    .sortByKey(ascending=False)

# Create an RDD with a separator line for the final output
delimiter = ["=========="]
delimiter_rdd = sc.parallelize(delimiter)  # Single-line RDD

# Concatenate all RDDs with separators in between
final_rdd = employees_formatted.union(delimiter_rdd) \
    .union(departments) \
    .union(delimiter_rdd) \
    .union(joined_data) \
    .union(delimiter_rdd) \
    .union(sorted_employees)

# Print the final output (for testing/debugging)
for item in final_rdd.coalesce(1).collect():
    print(item)

# Save the final output to HDFS
final_rdd.coalesce(1).saveAsTextFile(output_dir)
