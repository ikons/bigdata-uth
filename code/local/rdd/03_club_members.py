import os
import sys

from pyspark.sql import SparkSession

# Keep the Python executable consistent between the driver and Spark tasks.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = (
        # We intentionally use the simplest local setup so students can focus on the RDD operations.
        SparkSession.builder.master("local[*]")
        .config("spark.submit.deployMode", "client")
        .appName("club-members")
        .getOrCreate()
    )
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    # Each file contains one student name per line, so each RDD element is one student.
    python_club = sc.textFile("examples/club_python.txt")
    robotics_club = sc.textFile("examples/club_robotics.txt")

    # union() concatenates two RDDs without removing duplicates.
    all_students = python_club.union(robotics_club)

    # distinct() removes duplicates after the union.
    unique_students = all_students.distinct().sortBy(lambda name: name)

    # intersection() keeps only the values that appear in both RDDs.
    common_students = python_club.intersection(robotics_club).sortBy(
        lambda name: name
    )

    # collect() is safe because the club lists are tiny.
    print("Students in at least one club:", unique_students.collect())
    print("Students in both clubs:", common_students.collect())

    spark.stop()


if __name__ == "__main__":
    main()
