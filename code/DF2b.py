from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as sum_
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

# Keep the Python executable the same on the driver and on Spark workers.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Explicit schemas help us focus on the transformation logic instead of type inference.
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


def write_local_csv_output(output_path: str, rows: list[tuple[str, int]]) -> None:
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "part-00000")
    with open(output_file, "w", encoding="utf-8") as file_handle:
        for row in rows:
            file_handle.write(",".join(str(value) for value in row) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute the salary sum per department using the DataFrame API.",
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

    builder = SparkSession.builder.appName("DF query 2b execution")
    # Local files trigger a local session; remote paths reuse the cluster configuration.
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
        output_path = build_path(args.base_path, f"DF2b_{spark.sparkContext.applicationId}")

    # read.csv(..., schema=...) gives us a typed DataFrame immediately.
    employees_df = spark.read.csv(employees_path, schema=EMPLOYEES_SCHEMA)
    departments_df = spark.read.csv(departments_path, schema=DEPARTMENTS_SCHEMA)

    totals_by_department = (
        # First enrich each employee row with the readable department name.
        employees_df.join(departments_df, employees_df.dep_id == departments_df.id, "inner")
        # groupBy() defines one group per department and agg() computes the total salary per group.
        .groupBy("department")
        .agg(sum_("salary").alias("total_salary"))
        .orderBy(col("total_salary").desc(), col("department"))
    )

    # collect() is safe because the result has one row per department.
    results = [(row.department, row.total_salary) for row in totals_by_department.collect()]
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # A single output file is convenient in a teaching lab.
            totals_by_department.coalesce(1).write.mode("overwrite").csv(output_path)
        else:
            write_local_csv_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
