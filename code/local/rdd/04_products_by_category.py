import os
import sys

from pyspark.sql import SparkSession

# Keep the Python executable consistent between the driver and Spark tasks.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = (
        # local[*] is enough here because the goal is to understand grouping logic, not cluster deployment.
        SparkSession.builder.master("local[*]")
        .config("spark.submit.deployMode", "client")
        .appName("products-by-category")
        .getOrCreate()
    )
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    # In RDD examples we parse CSV rows manually, so every record starts as a list of strings.
    product_rows = sc.textFile("examples/products.csv").map(lambda line: line.split(","))

    # The category becomes the key because we want one result group per category.
    products_by_category = product_rows.map(lambda row: (row[2], row[1]))

    # groupByKey() is easy to read for small teaching examples.
    # For large production workloads, reduceByKey()/aggregateByKey() are often better choices.
    grouped_products = products_by_category.groupByKey()

    sorted_product_lists = grouped_products.mapValues(
        lambda names: sorted(list(names))
    )

    # sortByKey() makes the final output easier to read when categories are shown alphabetically.
    sorted_categories = sorted_product_lists.sortByKey()

    # collect() is fine because the grouped result is intentionally small.
    print(sorted_categories.collect())

    spark.stop()


if __name__ == "__main__":
    main()
