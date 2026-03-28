from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

# Keep the Python executable the same on the driver and on Spark workers.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# These schemas match SQLQ2.py so old references still produce the same typed result.
EMPLOYEES_SCHEMA = StructType(
    [
        StructField("id", IntegerType()),
        StructField("name", StringType()),
        StructField("salary", IntegerType()),
        StructField("dep_id", IntegerType()),
    ]
)

DEPARTMENTS_SCHEMA = StructType(
    [
        StructField("id", IntegerType()),
        StructField("department", StringType()),
    ]
)


def build_path(base_path: str, relative_path: str) -> str:
    return f"{base_path.rstrip('/')}/{relative_path.lstrip('/')}"


def write_local_csv_output(output_path: str, rows: list[tuple[int, str, int, str]]) -> None:
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "part-00000")
    with open(output_file, "w", encoding="utf-8") as file_handle:
        for row in rows:
            file_handle.write(",".join(str(value) for value in row) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Deprecated compatibility alias for the Spark SQL implementation of query 2.",
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

    builder = SparkSession.builder.appName("Deprecated query 2 SQL alias")
    # This file remains for backwards compatibility, but the canonical SQL solution is SQLQ2.py.
    if args.master:
        builder = builder.master(args.master)
        if args.master.startswith("local"):
            builder = builder.config("spark.submit.deployMode", "client")
    elif "://" not in employees_path and "://" not in departments_path:
        builder = builder.master("local[*]").config("spark.submit.deployMode", "client")

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    output_path = args.output
    if output_path is None and args.base_path:
        output_path = build_path(args.base_path, f"DFQ2_noI_{spark.sparkContext.applicationId}")

    employees_df = spark.read.csv(employees_path, schema=EMPLOYEES_SCHEMA)
    departments_df = spark.read.csv(departments_path, schema=DEPARTMENTS_SCHEMA)
    # SQL in Spark runs over temporary views created from DataFrames.
    employees_df.createOrReplaceTempView("employees")
    departments_df.createOrReplaceTempView("departments")

    # Keep the SQL text identical to SQLQ2.py so old references still produce the same result.
    query = """
        SELECT employees.id, employees.name, employees.salary, departments.department
        FROM employees
        INNER JOIN departments ON employees.dep_id = departments.id
        WHERE departments.department = 'Dep A'
        ORDER BY employees.salary DESC, employees.id ASC
        LIMIT 3
    """
    result_df = spark.sql(query)

    # collect() is safe because this compatibility alias still returns only 3 rows.
    results = [(row.id, row.name, row.salary, row.department) for row in result_df.collect()]
    print("Deprecated: use SQLQ2.py for the canonical Spark SQL implementation of query 2.")
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # overwrite keeps reruns simple for students.
            result_df.coalesce(1).write.mode("overwrite").csv(output_path)
        else:
            write_local_csv_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
