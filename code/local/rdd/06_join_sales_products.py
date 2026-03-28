import os
import sys

from pyspark.sql import SparkSession

# Keep the Python executable consistent between the driver and Spark tasks.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = (
        # This example introduces the classic Spark join pattern with two keyed RDDs.
        SparkSession.builder.master("local[*]")
        .config("spark.submit.deployMode", "client")
        .appName("join-sales-products")
        .getOrCreate()
    )
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    # sales.csv gives transactional data; products.csv gives the lookup information we need for enrichment.
    sale_rows = sc.textFile("examples/sales.csv").map(lambda line: line.split(","))

    sales_by_product = sale_rows.map(
        lambda row: (row[1], int(row[2]) * float(row[3]))
    )  # Use product_id as the key because that is the field we will join on.

    product_rows = sc.textFile("examples/products.csv").map(lambda line: line.split(","))

    products_by_id = product_rows.map(
        lambda row: (row[0], (row[1], row[2]))
    )  # Again, both RDDs must share the same key before join().

    # join() combines the values of both RDDs for matching product ids.
    joined_data = sales_by_product.join(products_by_id)

    revenue_by_category_pairs = joined_data.map(
        lambda item: (item[1][1][1], item[1][0])
    )  # After the join, switch the key from product_id to category.

    # Once the key becomes the category, reduceByKey() can sum all sales inside that category.
    category_totals = revenue_by_category_pairs.reduceByKey(
        lambda left, right: left + right
    )

    rounded_totals = category_totals.map(
        lambda item: (item[0], round(item[1], 2))
    )

    sorted_totals = rounded_totals.sortBy(
        lambda item: (-item[1], item[0])
    )

    # collect() is safe here because we only have one row per category.
    results = sorted_totals.collect()

    for item in results:
        print(item)

    os.makedirs("output", exist_ok=True)
    output_file = "output/category_revenue_local.txt"

    with open(output_file, "w", encoding="utf-8") as file_handle:
        # Saving a plain text file keeps the result easy to inspect outside Spark as well.
        for category, value in results:
            file_handle.write(f"{category},{value:.2f}\n")

    print(f"Saved to: {output_file}")

    spark.stop()


if __name__ == "__main__":
    main()
