import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("parallelize-basics").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    numbers = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4)  # Create a small RDD from a Python list.

    even_numbers = numbers.filter(lambda x: x % 2 == 0)  # Keep only the even numbers.

    squared_numbers = even_numbers.map(lambda x: (x, x * x))  # Turn each number into (number, square).

    sorted_numbers = squared_numbers.sortBy(
        lambda item: item[1],
        ascending=False,
    )  # Sort by the square value from largest to smallest.

    total_sum = numbers.reduce(lambda left, right: left + right)  # Add all numbers in the original RDD.

    print("Partitions:", numbers.getNumPartitions())
    print("Even squares:", sorted_numbers.collect())
    print("Sum:", total_sum)

    spark.stop()


if __name__ == "__main__":
    main()
