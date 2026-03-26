import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("join-sales-products").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    sale_rows = sc.textFile("examples/sales.csv").map(
        lambda line: line.split(",")
    )  # Split each sale line into columns.

    sales_by_product = sale_rows.map(
        lambda row: (row[1], int(row[2]) * float(row[3]))
    )  # Turn each sale into (product_id, sale_value).

    product_rows = sc.textFile("examples/products.csv").map(
        lambda line: line.split(",")
    )  # Split each product line into columns.

    products_by_id = product_rows.map(
        lambda row: (row[0], (row[1], row[2]))
    )  # Turn each product into (product_id, (product_name, category)).

    joined_data = sales_by_product.join(products_by_id)  # Match each sale with its product information.

    revenue_by_category_pairs = joined_data.map(
        lambda item: (item[1][1][1], item[1][0])
    )  # Turn each joined row into (category, sale_value).

    category_totals = revenue_by_category_pairs.reduceByKey(
        lambda left, right: left + right
    )  # Add all sale values for the same category.

    rounded_totals = category_totals.map(
        lambda item: (item[0], round(item[1], 2))
    )  # Round the totals for cleaner output.

    sorted_totals = rounded_totals.sortBy(
        lambda item: (-item[1], item[0])
    )  # Show the highest category total first.

    results = sorted_totals.collect()  # Bring the small result back to the driver.

    for item in results:
        print(item)

    os.makedirs("output", exist_ok=True)
    output_file = "output/category_revenue_local.txt"

    with open(output_file, "w", encoding="utf-8") as file_handle:
        for category, value in results:
            file_handle.write(f"{category},{value:.2f}\n")  # Write one line per result.

    print(f"Saved to: {output_file}")

    spark.stop()


if __name__ == "__main__":
    main()
