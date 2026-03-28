import os
import sys

from pyspark.sql import SparkSession

# Keep the Python executable consistent between the driver and Spark tasks.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = (
        # This is still a local example, but now the data is more "tabular" and closer to real workloads.
        SparkSession.builder.master("local[*]")
        .config("spark.submit.deployMode", "client")
        .appName("sales-filter-sort")
        .getOrCreate()
    )
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    # Each CSV line becomes a list of strings, so we convert numeric columns ourselves.
    rows = sc.textFile("examples/sales.csv").map(lambda line: line.split(","))

    sales = rows.map(
        lambda row: (
            row[0],
            row[1],
            int(row[2]),
            float(row[3]),
            row[4],
            int(row[2]) * float(row[3]),
        )
    )  # Build a richer tuple that already contains the derived total sale value.

    # filter() keeps only the rows that match a business rule.
    high_value_sales = sales.filter(lambda row: row[5] >= 20.0)

    # After filtering, we project only the columns we want to show to the user.
    selected_columns = high_value_sales.map(
        lambda row: (row[0], row[1], row[4], row[5])
    )

    # Sorting by a tuple lets us express both the main order and a tie-breaker.
    sorted_sales = selected_columns.sortBy(lambda row: (-row[3], row[0]))

    # collect() is acceptable because the lab dataset is tiny.
    for item in sorted_sales.collect():
        print(item)

    spark.stop()


if __name__ == "__main__":
    main()
