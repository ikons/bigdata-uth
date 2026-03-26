import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("sales-filter-sort").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    rows = sc.textFile("examples/sales.csv").map(lambda line: line.split(","))  # Split each CSV line into columns.

    sales = rows.map(
        lambda row: (
            row[0],
            row[1],
            int(row[2]),
            float(row[3]),
            row[4],
            int(row[2]) * float(row[3]),
        )
    )  # Build (sale_id, product_id, quantity, unit_price, city, total_value).

    high_value_sales = sales.filter(lambda row: row[5] >= 20.0)  # Keep only sales with total value at least 20.

    selected_columns = high_value_sales.map(
        lambda row: (row[0], row[1], row[4], row[5])
    )  # Keep only the columns we want to display.

    sorted_sales = selected_columns.sortBy(lambda row: (-row[3], row[0]))  # Show the highest-value sales first.

    for item in sorted_sales.collect():
        print(item)

    spark.stop()


if __name__ == "__main__":
    main()
