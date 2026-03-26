import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("products-by-category").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    product_rows = sc.textFile("examples/products.csv").map(
        lambda line: line.split(",")
    )  # Split each CSV line into columns.

    products_by_category = product_rows.map(lambda row: (row[2], row[1]))  # Turn each row into (category, product_name).

    grouped_products = products_by_category.groupByKey()  # Group the product names by category.

    sorted_product_lists = grouped_products.mapValues(
        lambda names: sorted(list(names))
    )  # Convert the grouped values into sorted Python lists.

    sorted_categories = sorted_product_lists.sortByKey()  # Sort by category name.

    print(sorted_categories.collect())

    spark.stop()


if __name__ == "__main__":
    main()
