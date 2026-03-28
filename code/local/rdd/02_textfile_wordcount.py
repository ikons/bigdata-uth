import os
import sys

from pyspark.sql import SparkSession

# Keep the Python executable consistent between the driver and Spark tasks.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = (
        # We stay in local client mode because this example is meant for first contact with Spark.
        SparkSession.builder.master("local[*]")
        .config("spark.submit.deployMode", "client")
        .appName("textfile-wordcount")
        .getOrCreate()
    )
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    # textFile() creates an RDD where each element is one line from the file.
    lines = sc.textFile("examples/text.txt")

    # flatMap() is useful when one input record can produce many outputs.
    words = lines.flatMap(lambda line: line.split())

    # Key-value pairs are the standard input shape for reduceByKey().
    word_pairs = words.map(lambda word: (word, 1))

    # reduceByKey() aggregates records that share the same key.
    word_counts = word_pairs.reduceByKey(lambda left, right: left + right)

    # The secondary sort by the word itself makes ties deterministic.
    sorted_word_counts = word_counts.sortBy(lambda item: (-item[1], item[0]))

    # collect() is safe because the example file is intentionally tiny.
    for item in sorted_word_counts.collect():
        print(item)

    spark.stop()


if __name__ == "__main__":
    main()
