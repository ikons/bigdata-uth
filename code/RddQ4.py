from pyspark.sql import SparkSession

# Create SparkContext
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

rdd_a = sc.parallelize(data_a)
rdd_b = sc.parallelize(data_b)

# --------------------------
# Prepare for join
# --------------------------

# Create key-value pairs using department_id as the key
# and add a dataset tag (1 for A, 2 for B)

# From Dataset A:
# (department_id, (1, (employee_id, employee_name, department_id)))
left = rdd_a.map(lambda x: (x[2], (1, x)))

# From Dataset B:
# (department_id, (2, (department_id, department_name)))
right = rdd_b.map(lambda x: (x[0], (2, x)))

# --------------------------
# Union the two RDDs
# --------------------------

# Use union so that all records end up in the same RDD
unioned_data = left.union(right)

# --------------------------
# Group by department_id
# --------------------------

# Records with the same department_id are grouped together
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

    # Return every employee/department-name combination
    return [(employee, dept) for employee in left_origin for dept in right_origin]

# --------------------------
# Final join result
# --------------------------

# Use flatMapValues to unroll the results
joined = grouped.flatMapValues(lambda x: arrange(x))

# Returns: (department_id, ((employee_id, name, dept_id), (dept_id, dept_name)))
for record in joined.collect():
    print(record)
