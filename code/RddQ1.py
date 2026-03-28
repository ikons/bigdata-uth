from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession

# Keep the Python executable the same on the driver and on Spark workers.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def build_path(base_path: str, relative_path: str) -> str:
    return f"{base_path.rstrip('/')}/{relative_path.lstrip('/')}"


def write_local_text_output(output_path: str, rows: list[tuple[int, str, int, int]]) -> None:
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "part-00000")
    with open(output_file, "w", encoding="utf-8") as file_handle:
        for row in rows:
            file_handle.write(f"{row}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find the 5 employees with the lowest salary using RDDs.",
    )
    parser.add_argument("--base-path", help="Base path that contains examples/ and the default output location.")
    parser.add_argument("--employees", help="Explicit employees CSV path.")
    parser.add_argument("--output", help="Explicit output path.")
    parser.add_argument("--master", help="Optional Spark master.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    employees_path = args.employees or (
        build_path(args.base_path, "examples/employees.csv")
        if args.base_path
        else "examples/employees.csv"
    )

    builder = SparkSession.builder.appName("RDD query 1 execution")
    # The same script can run either:
    # - locally for practice
    # - remotely when spark-submit injects cluster settings
    if args.master:
        builder = builder.master(args.master)
        if args.master.startswith("local"):
            builder = builder.config("spark.submit.deployMode", "client")
    elif "://" not in employees_path:
        builder = builder.master("local[*]").config("spark.submit.deployMode", "client")

    spark = builder.getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    output_path = args.output
    if output_path is None and args.base_path:
        output_path = build_path(args.base_path, f"RddQ1_{sc.applicationId}")

    # RDD CSV handling is manual: each line starts as plain text and we split it ourselves.
    employees = sc.textFile(employees_path).map(lambda line: line.split(","))

    lowest_salaries = (
        # Convert the numeric fields early so sorting behaves numerically and not lexicographically.
        employees.map(lambda row: (int(row[2]), int(row[0]), row[1], int(row[3])))
        # takeOrdered() is a good fit for small "top N" style answers.
        .takeOrdered(5)
    )

    # We reorder the tuple back into a human-readable form before printing or saving it.
    results = [(employee_id, name, salary, dep_id) for salary, employee_id, name, dep_id in lowest_salaries]
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # Parallelizing the tiny final answer is fine for lab-sized outputs.
            sc.parallelize(results, 1).saveAsTextFile(output_path)
        else:
            write_local_text_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
