from pyspark.sql import SparkSession

# This file is a small join demo built from in-memory Python data.
# It is useful for understanding the mechanics of RDD joins before reading CSV files.

# Create the SparkContext.
sc = SparkSession \
    .builder \
    .appName("Join Datasets with RDD") \
    .getOrCreate() \
    .sparkContext

# MINIMIZE LOG OUTPUT
sc.setLogLevel("ERROR")

# --------------------------
# Initial data
# --------------------------

# Dataset A: (employee_id, employee_name, department_id)
data_a = [
    (1, "George K", 1),
    (2, "John T", 2),
    (3, "Mary M", 1),
    (4, "Jerry S", 3)
]

# Dataset B: (department_id, department_name)
data_b = [
    (1, "Dep A"),
    (2, "Dep B"),
    (3, "Dep C")
]

# --------------------------
# Create RDDs
# --------------------------

# parallelize() creates RDDs directly from Python collections that already exist in memory.
rdd_a = sc.parallelize(data_a)
rdd_b = sc.parallelize(data_b)

# --------------------------
# Prepare for join
# --------------------------

# Create key-value pairs using department_id as the key.
# The dataset tag tells us later whether a row came from the employee side or the department side.

# From Dataset A:
# (department_id, (1, (employee_id, employee_name, department_id)))
left = rdd_a.map(lambda x: (x[2], (1, x)))

# From Dataset B:
# (department_id, (2, (department_id, department_name)))
right = rdd_b.map(lambda x: (x[0], (2, x)))

# --------------------------
# Union the two RDDs
# --------------------------

# union() simply concatenates the two keyed datasets into one RDD.
unioned_data = left.union(right)

# --------------------------
# Group by department_id
# --------------------------

# groupByKey() brings together all rows that share the same department_id.
# This is a very explicit teaching approach for understanding joins, even if it is not the most efficient one.
grouped = unioned_data.groupByKey()

# --------------------------
# Function for merging the data
# --------------------------

def arrange(records):
    left_origin = []   # Records from Dataset A (employees)
    right_origin = []  # Records from Dataset B (departments)

    for (source_id, value) in records:
        if source_id == 1:
            left_origin.append(value)
        elif source_id == 2:
            right_origin.append(value)

    # Return every employee/department-name combination for one department id.
    return [(employee, dept) for employee in left_origin for dept in right_origin]

# --------------------------
# Final join result
# --------------------------

# flatMapValues() keeps the key and emits one output row for every join match.
# The final shape is similar to a join result produced by relational systems.
joined = grouped.flatMapValues(lambda x: arrange(x))

# collect() is safe here because the in-memory demo is tiny.
# Returns: (department_id, ((employee_id, name, dept_id), (dept_id, dept_name)))
for record in joined.collect():
    print(record)
