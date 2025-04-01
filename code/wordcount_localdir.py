from pyspark import SparkContext

# Initialize SparkContext
sc = SparkContext(appName="WordCount")

# Read all files in the HDFS directory
#input_dir = "hdfs://hdfs-namenode:9000/data/CC-MAIN-20241201162023-20241201192023-00000.warc.wet"
input_dir = "hdfs://hdfs-namenode:9000/data"
# Get the application ID (job ID) from the Spark context
job_id = sc.applicationId

# Create the dynamic output directory by appending the job ID
output_dir = f"hdfs://hdfs-namenode:9000/user/ikons/wordcount_output_{job_id}"

# Perform the word count operation
text_files = sc.textFile(input_dir)

#sampled_text = text_files.sample(withReplacement=False, fraction=0.001, seed=42)

# Split lines into words, map them to (word, 1) pairs, then reduce by key
word_count = text_files.flatMap(lambda line: line.split(" ")) \
                       .map(lambda word: (word, 1)) \
                       .reduceByKey(lambda a, b: a + b)


# Sort the results by occurrences in decreasing order
sorted_word_count = word_count.map(lambda x: (x[1], x[0])) \
                               .sortByKey(ascending=False) \
                               .map(lambda x: (x[1], x[0]))

# Save the sorted results directly to HDFS in a single output file
sorted_word_count.coalesce(1).saveAsTextFile(output_dir)

