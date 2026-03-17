from pyspark.sql import SparkSession
username = "ikons"
sc = SparkSession \
    .builder \
    .appName("wordcount example") \
    .getOrCreate() \
    .sparkContext

# MINIMIZE LOG OUTPUT
sc.setLogLevel("ERROR")

# Retrieve the job ID and define the output path
job_id = sc.applicationId
output_dir = f"hdfs://hdfs-namenode:9000/user/{username}/wordcount_output_{job_id}"

# Load the text file from HDFS and compute word frequencies
wordcount = (
    sc.textFile(f"hdfs://hdfs-namenode:9000/user/{username}/examples/text.txt") \
    .flatMap(lambda x: x.split(" "))                 # Split each line into words
    .map(lambda x: (x, 1))                           # Map each word to (word, 1)
    .reduceByKey(lambda x, y: x + y)                 # Sum occurrences for each word
    .sortBy(lambda x: x[1], ascending=False)         # Sort by frequency in descending order
)

# Print the results (for verification)
for item in wordcount.coalesce(1).collect():
    print(item)

# Coalesce to reduce the number of output files and save to HDFS
wordcount.saveAsTextFile(output_dir)

# Example output:
# [('text', 3), ('this', 2), ('is', 2), ('like', 2), ('a', 2),
#  ('file', 2), ('words', 2), (',', 2), ('an', 1), ('of', 1),
#  ('with', 1), ('random', 1), ('example', 1)]
