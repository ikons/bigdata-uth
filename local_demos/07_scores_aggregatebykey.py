import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("scores-aggregatebykey").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    score_rows = sc.textFile("examples/scores.csv").map(
        lambda line: line.split(",")
    )  # Split each CSV line into columns.

    scores_by_course = score_rows.map(lambda row: (row[1], int(row[2])))  # Turn each row into (course, score).

    sums_and_counts = scores_by_course.aggregateByKey(
        (0, 0),
        lambda acc, score: (acc[0] + score, acc[1] + 1),
        lambda left, right: (left[0] + right[0], left[1] + right[1]),
    )  # Keep track of (sum_of_scores, number_of_scores) for each course.

    averages = sums_and_counts.mapValues(
        lambda item: round(item[0] / item[1], 2)
    )  # Turn each (sum, count) pair into an average.

    sorted_averages = averages.sortBy(
        lambda item: (-item[1], item[0])
    )  # Show the highest average first.

    for item in sorted_averages.collect():
        print(item)

    spark.stop()


if __name__ == "__main__":
    main()
