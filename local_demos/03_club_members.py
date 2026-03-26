import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("club-members").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    python_club = sc.textFile("examples/club_python.txt")  # Read the first club list.
    robotics_club = sc.textFile("examples/club_robotics.txt")  # Read the second club list.

    all_students = python_club.union(robotics_club)  # Combine the two club lists into one RDD.

    unique_students = all_students.distinct().sortBy(lambda name: name)  # Keep each student only once.

    common_students = python_club.intersection(robotics_club).sortBy(
        lambda name: name
    )  # Keep only students who appear in both lists.

    print("Students in at least one club:", unique_students.collect())
    print("Students in both clubs:", common_students.collect())

    spark.stop()


if __name__ == "__main__":
    main()
