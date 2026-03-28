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


def write_local_text_output(output_path: str, rows: list[tuple[int, str, int, str]]) -> None:
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "part-00000")
    with open(output_file, "w", encoding="utf-8") as file_handle:
        for row in rows:
            file_handle.write(f"{row}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find the 3 highest-paid employees in Dep A using RDDs.",
    )
    parser.add_argument("--base-path", help="Base path that contains examples/ and the default output location.")
    parser.add_argument("--employees", help="Explicit employees CSV path.")
    parser.add_argument("--departments", help="Explicit departments CSV path.")
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
    departments_path = args.departments or (
        build_path(args.base_path, "examples/departments.csv")
        if args.base_path
        else "examples/departments.csv"
    )

    builder = SparkSession.builder.appName("RDD query 2 execution")
    # Run locally when the inputs are local files; otherwise reuse the cluster settings from spark-submit.
    if args.master:
        builder = builder.master(args.master)
        if args.master.startswith("local"):
            builder = builder.config("spark.submit.deployMode", "client")
    elif "://" not in employees_path and "://" not in departments_path:
        builder = builder.master("local[*]").config("spark.submit.deployMode", "client")

    spark = builder.getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    output_path = args.output
    if output_path is None and args.base_path:
        output_path = build_path(args.base_path, f"RddQ2_{sc.applicationId}")

    # With RDDs we parse the CSV rows ourselves, so every field starts as a string.
    employees = sc.textFile(employees_path).map(lambda line: line.split(","))
    departments = sc.textFile(departments_path).map(lambda line: line.split(","))

    # To perform an RDD join, both datasets must be keyed by the same join key.
    # Here the common key is the department id.
    dep_a_ids = departments.filter(lambda row: row[1] == "Dep A").map(lambda row: (row[0], row[1]))
    employees_by_department = employees.map(lambda row: (row[3], (int(row[0]), row[1], int(row[2]))))

    top_employees = (
        # join() keeps only matching department ids from both RDDs.
        employees_by_department.join(dep_a_ids)
        # Rearrange the joined record so salary comes first and can drive the ordering.
        .map(lambda item: (item[1][0][2], item[1][0][0], item[1][0][1], item[1][1]))
        # Highest salary first, then employee id as a stable tie-breaker.
        .takeOrdered(3, key=lambda item: (-item[0], item[1]))
    )

    results = [(employee_id, name, salary, department) for salary, employee_id, name, department in top_employees]
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # Saving the tiny result through parallelize() is enough for a teaching example.
            sc.parallelize(results, 1).saveAsTextFile(output_path)
        else:
            write_local_text_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
