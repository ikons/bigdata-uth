import os
import sys

from pyspark.sql import SparkSession

# Keep the Python executable consistent between the driver and Spark tasks.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = (
        # This example is useful when students are ready to move beyond reduceByKey().
        SparkSession.builder.master("local[*]")
        .config("spark.submit.deployMode", "client")
        .appName("scores-aggregatebykey")
        .getOrCreate()
    )
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    # Each row contains a student, a course, and a score.
    score_rows = sc.textFile("examples/scores.csv").map(lambda line: line.split(","))

    # The course becomes the key because we want one aggregate per course.
    scores_by_course = score_rows.map(lambda row: (row[1], int(row[2])))

    sums_and_counts = scores_by_course.aggregateByKey(
        (0, 0),
        # The zero value is the initial accumulator for each key: (sum, count).
        # seqOp: update the accumulator inside one partition.
        lambda acc, score: (acc[0] + score, acc[1] + 1),
        # combOp: merge partial accumulators coming from different partitions.
        lambda left, right: (left[0] + right[0], left[1] + right[1]),
    )

    averages = sums_and_counts.mapValues(
        lambda item: round(item[0] / item[1], 2)
    )  # Convert each (sum, count) pair into the final average.

    sorted_averages = averages.sortBy(
        lambda item: (-item[1], item[0])
    )

    # collect() is fine because the result has one row per course.
    for item in sorted_averages.collect():
        print(item)

    spark.stop()


if __name__ == "__main__":
    main()
