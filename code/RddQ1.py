from pyspark.sql import SparkSession

username = "ikons"
sc = SparkSession \
    .builder \
    .appName("RDD query 1 execution") \
    .getOrCreate() \
    .sparkContext

# MINIMIZE LOG OUTPUT
sc.setLogLevel("ERROR")

# Retrieve the job ID and define the output path
job_id = sc.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/RddQ1_{job_id}"

# Load and preprocess data
# CSV columns: "id", "name", "salary", "dep_id"
employees = sc.textFile(f"hdfs://hdfs-namenode:9000/user/{username}/examples/employees.csv") \
    .map(lambda x: x.split(","))  # Split each line into a list

# Map each employee to the form (salary, [id, name, dep_id]) and sort by salary (ascending)
# Column mapping:
#   x[0] = id
#   x[1] = name
#   x[2] = salary
#   x[3] = dep_id
sorted_employees = employees.map(lambda x: [int(x[2]), [x[0], x[1], x[3]]]) \
    .sortByKey()

# Print the data (for verification)
for item in sorted_employees.coalesce(1).collect():
    print(item)  # Example output: [60000, ['123', 'Alice', '5']]

# Coalesce to reduce the number of output files and save to HDFS
sorted_employees.coalesce(1).saveAsTextFile(output_dir)
