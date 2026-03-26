import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("textfile-wordcount").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    lines = sc.textFile("examples/text.txt")  # Read the input file line by line.

    words = lines.flatMap(lambda line: line.split())  # Split each line into separate words.

    word_pairs = words.map(lambda word: (word, 1))  # Turn each word into (word, 1).

    word_counts = word_pairs.reduceByKey(lambda left, right: left + right)  # Add the counts for the same word.

    sorted_word_counts = word_counts.sortBy(lambda item: (-item[1], item[0]))  # Show the most frequent words first.

    for item in sorted_word_counts.collect():
        print(item)

    spark.stop()


if __name__ == "__main__":
    main()
