import os
import sys

from pyspark.sql import SparkSession

# Keep the Python executable consistent between the driver and Spark tasks.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = (
        # local[*] uses all local CPU cores and is the simplest setup for practice.
        SparkSession.builder.master("local[*]")
        .config("spark.submit.deployMode", "client")
        .appName("parallelize-basics")
        .getOrCreate()
    )
    # The SparkSession is the main entry point; from it we access the SparkContext for RDD work.
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    # parallelize() creates an RDD directly from data that already exists in Python memory.
    numbers = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4)

    # filter() keeps only the records that satisfy the predicate.
    even_numbers = numbers.filter(lambda x: x % 2 == 0)

    # map() transforms each input record into exactly one output record.
    squared_numbers = even_numbers.map(lambda x: (x, x * x))

    sorted_numbers = squared_numbers.sortBy(
        lambda item: item[1],
        ascending=False,
    )  # Sorting is another transformation, so nothing runs yet.

    # reduce() is an action: it triggers execution and combines all elements into one value.
    total_sum = numbers.reduce(lambda left, right: left + right)

    # getNumPartitions() helps students connect the logical RDD with Spark's parallel execution units.
    print("Partitions:", numbers.getNumPartitions())
    # collect() is acceptable here because the result is tiny.
    print("Even squares:", sorted_numbers.collect())
    print("Sum:", total_sum)

    spark.stop()


if __name__ == "__main__":
    main()
