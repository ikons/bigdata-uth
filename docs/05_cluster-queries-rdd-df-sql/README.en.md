# The same queries on the cluster with RDD, the DataFrame API, and Spark SQL

This guide builds on the local guides in `docs/02_vscode-local-authoring`, `docs/02_pycharm-local-authoring`, and `docs/03_local-spark-workbook` and carries the same questions into remote execution.

It runs only from WSL, on top of the environment configured in `04_remote-spark-kubernetes`.

The core idea is:

- the question stays the same
- the reference script stays the same
- only the execution method and data paths change

This keeps the student from learning a new API and new infrastructure at the same time.

## What you will learn

By the end of this lab you will be able to:

- run Spark jobs from your own WSL environment through the VPN
- read data from HDFS with `--base-path`
- compare RDD, the DataFrame API, and Spark SQL on the same datasets
- distinguish core questions from extra and appendix examples

## Before you start

Recommended order:

1. [docs/02_vscode-local-authoring/README.en.md](../02_vscode-local-authoring/README.en.md)
2. alternatively [docs/02_pycharm-local-authoring/README.en.md](../02_pycharm-local-authoring/README.en.md)
3. [docs/03_local-spark-workbook/README.en.md](../03_local-spark-workbook/README.en.md)
4. [docs/04_remote-spark-kubernetes/README.en.md](../04_remote-spark-kubernetes/README.en.md) for the Kubernetes execution path

This guide assumes that:

- you have completed the WSL/VPN setup from the [remote Spark execution guide for Kubernetes](../04_remote-spark-kubernetes/README.en.md)
- `spark-submit`, `kubectl`, and `hdfs` are already on `PATH`
- a per-user `spark-defaults.conf` already targets the lab cluster
- your HDFS user namespace is available

If you are coming directly from the local workbook, first leave `.venv` and reload the WSL Spark environment:

```bash
deactivate 2>/dev/null || true
source ~/bigdata-env.sh
hash -r
command -v spark-submit
```

## The data and the reference scripts

The main data files are:

- `examples/employees.csv`
- `examples/departments.csv`
- `examples/text.txt`

The reference scripts are:

| Question | RDD | DataFrame API | Spark SQL |
| --- | --- | --- | --- |
| Q1: 5 lowest salaries | `code/RddQ1.py` | `code/DFQ1.py` | `code/SQLQ1.py` |
| Q2: 3 highest-paid employees in Dep A | `code/RddQ2.py` | `code/DFQ2.py` | `code/SQLQ2.py` |
| Q3: yearly income | `code/RddQ3.py` | `code/DFQ3.py` | `code/SQLQ3.py` |

Additional examples:

- `code/wordcount.py`
- `code/DF2b.py`
- `code/DFQ3_udf.py`

Appendix:

- `code/RddQ4.py`

## Upload to HDFS

From your WSL terminal:

```bash
cd ~/bigdata-uth
hadoop fs -rm -r -f /user/$USER/examples /user/$USER/code || true
hadoop fs -mkdir -p /user/$USER/examples /user/$USER/code
hadoop fs -put -f examples/* /user/$USER/examples/
hadoop fs -put -f code/*.py /user/$USER/code/

hadoop fs -ls /user/$USER/examples
hadoop fs -ls /user/$USER/code
```

The cleanup line is optional, but useful when you rerun the same lab and want clean, predictable HDFS inputs.

## The execution pattern

The shared execution pattern for all reference scripts is:

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/<script>.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

With this:

- the code runs without hardcoded usernames
- data is read from `hdfs://.../examples/...`
- output is written automatically to a path containing the `applicationId`

Important:

- with the per-user `spark-defaults.conf` from the [remote Spark execution guide for Kubernetes](../04_remote-spark-kubernetes/README.en.md), plain `spark-submit` in WSL already runs on Kubernetes in cluster mode
- if you want to bypass that setup temporarily, you can override it explicitly with another `--master` or `--deploy-mode`

## Introductory example: Word Count

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/wordcount.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/wordcount.py -->
``` python
from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession

# Keep the Python executable the same on the driver and on Spark workers.
# This avoids subtle version mismatches when the same script runs locally or on a cluster.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def build_path(base_path: str, relative_path: str) -> str:
    return f"{base_path.rstrip('/')}/{relative_path.lstrip('/')}"


def write_local_text_output(output_path: str, lines: list[str]) -> None:
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "part-00000")
    with open(output_file, "w", encoding="utf-8") as file_handle:
        for line in lines:
            file_handle.write(f"{line}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count word frequencies from a text file with Spark.",
    )
    parser.add_argument(
        "--base-path",
        help="Base path that contains examples/ and where outputs should be written.",
    )
    parser.add_argument(
        "--input",
        help="Explicit input text path. Defaults to examples/text.txt locally or <base-path>/examples/text.txt remotely.",
    )
    parser.add_argument(
        "--output",
        help="Explicit output path. If omitted, local runs only print results and remote runs write under <base-path>.",
    )
    parser.add_argument(
        "--master",
        help="Optional Spark master. Local runs default to local[*] when no remote path is used.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = args.input or (
        build_path(args.base_path, "examples/text.txt")
        if args.base_path
        else "examples/text.txt"
    )

    builder = SparkSession.builder.appName("wordcount example")
    # Reuse the same script in two contexts:
    # - local files -> start a local Spark session
    # - remote URIs -> let spark-submit use the external cluster configuration
    if args.master:
        builder = builder.master(args.master)
        if args.master.startswith("local"):
            builder = builder.config("spark.submit.deployMode", "client")
    elif "://" not in input_path:
        builder = builder.master("local[*]").config("spark.submit.deployMode", "client")

    spark = builder.getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    output_path = args.output
    if output_path is None and args.base_path:
        output_path = build_path(args.base_path, f"wordcount_output_{sc.applicationId}")

    wordcount = (
        # textFile() gives an RDD where each element is one line from the input file.
        sc.textFile(input_path)
        # flatMap() is the classic "one input record -> many output records" step.
        .flatMap(lambda line: line.split())
        .map(lambda word: (word, 1))
        # reduceByKey() is the standard RDD aggregation pattern for key-value data.
        .reduceByKey(lambda left, right: left + right)
        .sortBy(lambda item: (-item[1], item[0]))
    )

    # collect() is safe here because the lab output is intentionally small.
    results = wordcount.collect()
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # coalesce(1) makes the lab output easier to inspect.
            # For large real workloads, a single output partition would usually be a bottleneck.
            wordcount.coalesce(1).saveAsTextFile(output_path)
        else:
            write_local_text_output(output_path, [str(item) for item in results])
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
```
<!-- END AUTO-CODE -->

## Q1: 5 lowest salaries

The business question is the same in every API:

- read `employees.csv`
- sort by ascending salary
- keep only the first 5 rows

### Q1 with RDD

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/RddQ1.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/RddQ1.py -->
``` python
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
```
<!-- END AUTO-CODE -->

### Q1 with the DataFrame API

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/DFQ1.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/DFQ1.py -->
``` python
from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

# Keep the Python executable the same on the driver and on Spark workers.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Use an explicit schema so beginners can see the intended column types
# and Spark does not have to guess them from the data.
EMPLOYEES_SCHEMA = StructType(
    [
        StructField("id", IntegerType()),
        StructField("name", StringType()),
        StructField("salary", IntegerType()),
        StructField("dep_id", IntegerType()),
    ]
)


def build_path(base_path: str, relative_path: str) -> str:
    return f"{base_path.rstrip('/')}/{relative_path.lstrip('/')}"


def write_local_csv_output(output_path: str, rows: list[tuple[int, str, int, int]]) -> None:
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "part-00000")
    with open(output_file, "w", encoding="utf-8") as file_handle:
        for row in rows:
            file_handle.write(",".join(str(value) for value in row) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find the 5 employees with the lowest salary using the DataFrame API.",
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

    builder = SparkSession.builder.appName("DF query 1 execution")
    # The same script supports both local practice and remote submission.
    if args.master:
        builder = builder.master(args.master)
        if args.master.startswith("local"):
            builder = builder.config("spark.submit.deployMode", "client")
    elif "://" not in employees_path:
        builder = builder.master("local[*]").config("spark.submit.deployMode", "client")

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    output_path = args.output
    if output_path is None and args.base_path:
        output_path = build_path(args.base_path, f"DFQ1_{spark.sparkContext.applicationId}")

    # In the DataFrame API Spark already knows the columns by name and type.
    employees_df = spark.read.csv(employees_path, schema=EMPLOYEES_SCHEMA)
    lowest_salaries = (
        # orderBy() sorts the whole DataFrame, and limit() keeps only the first 5 rows after sorting.
        employees_df.orderBy(col("salary"), col("id"))
        .limit(5)
        .select("id", "name", "salary", "dep_id")
    )

    # collect() is fine here because the final answer only contains 5 rows.
    results = [(row.id, row.name, row.salary, row.dep_id) for row in lowest_salaries.collect()]
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # A single output file is convenient for lab inspection, but not for large jobs.
            lowest_salaries.coalesce(1).write.mode("overwrite").csv(output_path)
        else:
            write_local_csv_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
```
<!-- END AUTO-CODE -->

### Q1 with Spark SQL

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/SQLQ1.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/SQLQ1.py -->
``` python
from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

# Keep the Python executable the same on the driver and on Spark workers.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# The explicit schema keeps the SQL version aligned with the DataFrame version.
EMPLOYEES_SCHEMA = StructType(
    [
        StructField("id", IntegerType()),
        StructField("name", StringType()),
        StructField("salary", IntegerType()),
        StructField("dep_id", IntegerType()),
    ]
)


def build_path(base_path: str, relative_path: str) -> str:
    return f"{base_path.rstrip('/')}/{relative_path.lstrip('/')}"


def write_local_csv_output(output_path: str, rows: list[tuple[int, str, int, int]]) -> None:
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "part-00000")
    with open(output_file, "w", encoding="utf-8") as file_handle:
        for row in rows:
            file_handle.write(",".join(str(value) for value in row) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Find the 5 employees with the lowest salary using Spark SQL.",
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

    builder = SparkSession.builder.appName("SQL query 1 execution")
    # Local files imply local mode; remote URIs let spark-submit decide the cluster settings.
    if args.master:
        builder = builder.master(args.master)
        if args.master.startswith("local"):
            builder = builder.config("spark.submit.deployMode", "client")
    elif "://" not in employees_path:
        builder = builder.master("local[*]").config("spark.submit.deployMode", "client")

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    output_path = args.output
    if output_path is None and args.base_path:
        output_path = build_path(args.base_path, f"SQLQ1_{spark.sparkContext.applicationId}")

    # We still load CSV files as DataFrames first; SQL then works on top of those DataFrames via temp views.
    employees_df = spark.read.csv(employees_path, schema=EMPLOYEES_SCHEMA)
    # A temp view exposes the DataFrame to Spark SQL using a table-like name.
    employees_df.createOrReplaceTempView("employees")

    result_df = spark.sql(
        """
        SELECT id, name, salary, dep_id
        FROM employees
        ORDER BY salary ASC, id ASC
        LIMIT 5
        """
    )

    # collect() is safe because LIMIT 5 guarantees a tiny result.
    results = [(row.id, row.name, row.salary, row.dep_id) for row in result_df.collect()]
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # overwrite is convenient when students rerun the same query many times.
            result_df.coalesce(1).write.mode("overwrite").csv(output_path)
        else:
            write_local_csv_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
```
<!-- END AUTO-CODE -->

## Q2: 3 highest-paid employees in Dep A

The business question is:

- join employees and departments
- keep only `Dep A`
- sort by descending salary
- return only 3 rows

### Q2 with RDD

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/RddQ2.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/RddQ2.py -->
``` python
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
```
<!-- END AUTO-CODE -->

### Q2 with the DataFrame API

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/DFQ2.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/DFQ2.py -->
``` python
from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

# Keep the Python executable the same on the driver and on Spark workers.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Explicit schemas make joins easier to reason about because we know the type of each join column.
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
        description="Find the 3 highest-paid employees in Dep A using the DataFrame API.",
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

    builder = SparkSession.builder.appName("DF query 2 execution")
    # Decide between local mode and external cluster mode from the input paths.
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
        output_path = build_path(args.base_path, f"DFQ2_{spark.sparkContext.applicationId}")

    # Both CSV files become typed DataFrames, which makes the join expression much clearer than in raw RDD code.
    employees_df = spark.read.csv(employees_path, schema=EMPLOYEES_SCHEMA)
    departments_df = spark.read.csv(departments_path, schema=DEPARTMENTS_SCHEMA)

    result_df = (
        # DataFrame joins are expressed directly on named columns instead of manual key-value pairs.
        employees_df.join(departments_df, employees_df.dep_id == departments_df.id, "inner")
        # filter() keeps only rows from the target department.
        .filter(col("department") == "Dep A")
        .orderBy(col("salary").desc(), employees_df.id.asc())
        .select(employees_df.id.alias("id"), "name", "salary", "department")
        .limit(3)
    )

    # collect() is safe because the query keeps only 3 rows.
    results = [(row.id, row.name, row.salary, row.department) for row in result_df.collect()]
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # coalesce(1) is only for easier inspection of the final lab output.
            result_df.coalesce(1).write.mode("overwrite").csv(output_path)
        else:
            write_local_csv_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
```
<!-- END AUTO-CODE -->

### Q2 with Spark SQL

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/SQLQ2.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/SQLQ2.py -->
``` python
from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

# Keep the Python executable the same on the driver and on Spark workers.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# The schemas make the SQL example deterministic and comparable to the RDD and DataFrame versions.
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
        description="Find the 3 highest-paid employees in Dep A using Spark SQL.",
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

    builder = SparkSession.builder.appName("SQL query 2 execution")
    # Reuse the same script locally and remotely by inspecting the input paths.
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
        output_path = build_path(args.base_path, f"SQLQ2_{spark.sparkContext.applicationId}")

    employees_df = spark.read.csv(employees_path, schema=EMPLOYEES_SCHEMA)
    departments_df = spark.read.csv(departments_path, schema=DEPARTMENTS_SCHEMA)
    # The temp views are the bridge from DataFrame data to SQL syntax.
    employees_df.createOrReplaceTempView("employees")
    departments_df.createOrReplaceTempView("departments")

    result_df = spark.sql(
        """
        SELECT employees.id, employees.name, employees.salary, departments.department
        FROM employees
        INNER JOIN departments ON employees.dep_id = departments.id
        WHERE departments.department = 'Dep A'
        ORDER BY employees.salary DESC, employees.id ASC
        LIMIT 3
        """
    )

    # collect() is safe because LIMIT 3 keeps the output intentionally small.
    results = [(row.id, row.name, row.salary, row.department) for row in result_df.collect()]
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # coalesce(1) is only to simplify inspection of the final lab output.
            result_df.coalesce(1).write.mode("overwrite").csv(output_path)
        else:
            write_local_csv_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
```
<!-- END AUTO-CODE -->

## Q3: Yearly income

The business question is:

- compute `yearly_income = salary * 14`
- show the results sorted by descending yearly income

### Q3 with RDD

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/RddQ3.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/RddQ3.py -->
``` python
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


def write_local_text_output(output_path: str, rows: list[tuple[str, int]]) -> None:
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "part-00000")
    with open(output_file, "w", encoding="utf-8") as file_handle:
        for row in rows:
            file_handle.write(f"{row}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute yearly income for all employees using RDDs.",
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

    builder = SparkSession.builder.appName("RDD query 3 execution")
    # Reuse the same code locally and remotely by switching behavior based on the input path.
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
        output_path = build_path(args.base_path, f"RddQ3_{sc.applicationId}")

    results = (
        # In the RDD API we explicitly define the record shape step by step.
        sc.textFile(employees_path)
        .map(lambda line: line.split(","))
        # This transformation keeps only the name and the derived yearly income.
        .map(lambda row: (row[1], 14 * int(row[2])))
        .sortBy(lambda item: (-item[1], item[0]))
        # collect() is safe here because the example dataset is intentionally small.
        .collect()
    )

    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # A single output partition keeps the result easy to inspect.
            sc.parallelize(results, 1).saveAsTextFile(output_path)
        else:
            write_local_text_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
```
<!-- END AUTO-CODE -->

### Q3 with the DataFrame API

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/DFQ3.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/DFQ3.py -->
``` python
from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

# Keep the Python executable the same on the driver and on Spark workers.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Explicit types keep the example deterministic and easy to compare with the RDD and SQL versions.
EMPLOYEES_SCHEMA = StructType(
    [
        StructField("id", IntegerType()),
        StructField("name", StringType()),
        StructField("salary", IntegerType()),
        StructField("dep_id", IntegerType()),
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
        description="Compute yearly income for all employees using the DataFrame API.",
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

    builder = SparkSession.builder.appName("DF query 3 execution")
    # The same script can be reused locally or through spark-submit on a cluster.
    if args.master:
        builder = builder.master(args.master)
        if args.master.startswith("local"):
            builder = builder.config("spark.submit.deployMode", "client")
    elif "://" not in employees_path:
        builder = builder.master("local[*]").config("spark.submit.deployMode", "client")

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    output_path = args.output
    if output_path is None and args.base_path:
        output_path = build_path(args.base_path, f"DFQ3_{spark.sparkContext.applicationId}")

    employees_df = spark.read.csv(employees_path, schema=EMPLOYEES_SCHEMA)
    result_df = (
        # Prefer built-in column expressions when possible.
        # Spark can optimize them better than Python-level custom code.
        employees_df.select("name", (col("salary") * 14).alias("yearly_income"))
        .orderBy(col("yearly_income").desc(), col("name"))
    )

    # collect() is safe because the teaching dataset is small.
    results = [(row.name, row.yearly_income) for row in result_df.collect()]
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # A single CSV part is easier to inspect after a lab run.
            result_df.coalesce(1).write.mode("overwrite").csv(output_path)
        else:
            write_local_csv_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
```
<!-- END AUTO-CODE -->

### Q3 with Spark SQL

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/SQLQ3.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/SQLQ3.py -->
``` python
from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

# Keep the Python executable the same on the driver and on Spark workers.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Keep the schema explicit so the SQL and DataFrame versions behave the same way.
EMPLOYEES_SCHEMA = StructType(
    [
        StructField("id", IntegerType()),
        StructField("name", StringType()),
        StructField("salary", IntegerType()),
        StructField("dep_id", IntegerType()),
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
        description="Compute yearly income for all employees using Spark SQL.",
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

    builder = SparkSession.builder.appName("SQL query 3 execution")
    # Local input paths trigger local mode; remote paths keep the cluster mode configured by spark-submit.
    if args.master:
        builder = builder.master(args.master)
        if args.master.startswith("local"):
            builder = builder.config("spark.submit.deployMode", "client")
    elif "://" not in employees_path:
        builder = builder.master("local[*]").config("spark.submit.deployMode", "client")

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    output_path = args.output
    if output_path is None and args.base_path:
        output_path = build_path(args.base_path, f"SQLQ3_{spark.sparkContext.applicationId}")

    employees_df = spark.read.csv(employees_path, schema=EMPLOYEES_SCHEMA)
    # Spark SQL queries run against temporary views created from DataFrames.
    employees_df.createOrReplaceTempView("employees")

    result_df = spark.sql(
        """
        SELECT name, salary * 14 AS yearly_income
        FROM employees
        ORDER BY yearly_income DESC, name ASC
        """
    )

    # collect() is safe because the example dataset is small enough for teaching purposes.
    results = [(row.name, row.yearly_income) for row in result_df.collect()]
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # A single output file keeps the result easy to inspect after submission.
            result_df.coalesce(1).write.mode("overwrite").csv(output_path)
        else:
            write_local_csv_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
```
<!-- END AUTO-CODE -->

## Additional examples

### Salary sum per department with the DataFrame API

This is an additional tabular example and is not part of the main `Q1-Q3` core.

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/DF2b.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/DF2b.py -->
``` python
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
```
<!-- END AUTO-CODE -->

### The same Q3 with a DataFrame UDF

`DFQ3_udf.py` is retained as an additional example, not as the main DataFrame implementation of `Q3`.

```bash
spark-submit hdfs://hdfs-namenode:9000/user/$USER/code/DFQ3_udf.py \
  --base-path hdfs://hdfs-namenode:9000/user/$USER
```

<!-- AUTO-CODE: code/DFQ3_udf.py -->
``` python
from __future__ import annotations

import argparse
import os
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

# Keep the Python executable the same on the driver and on Spark workers.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# This schema is the same as in the other implementations so the results stay comparable.
EMPLOYEES_SCHEMA = StructType(
    [
        StructField("id", IntegerType()),
        StructField("name", StringType()),
        StructField("salary", IntegerType()),
        StructField("dep_id", IntegerType()),
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
        description="Compute yearly income for all employees using a DataFrame UDF.",
    )
    parser.add_argument("--base-path", help="Base path that contains examples/ and the default output location.")
    parser.add_argument("--employees", help="Explicit employees CSV path.")
    parser.add_argument("--output", help="Explicit output path.")
    parser.add_argument("--master", help="Optional Spark master.")
    return parser.parse_args()


def calculate_yearly_income(salary):
    # The UDF body is plain Python code.
    return 14 * salary


def main() -> None:
    args = parse_args()
    employees_path = args.employees or (
        build_path(args.base_path, "examples/employees.csv")
        if args.base_path
        else "examples/employees.csv"
    )

    builder = SparkSession.builder.appName("DF query 3 UDF execution")
    # The UDF example uses the same local/remote switching pattern as the other scripts.
    if args.master:
        builder = builder.master(args.master)
        if args.master.startswith("local"):
            builder = builder.config("spark.submit.deployMode", "client")
    elif "://" not in employees_path:
        builder = builder.master("local[*]").config("spark.submit.deployMode", "client")

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    output_path = args.output
    if output_path is None and args.base_path:
        output_path = build_path(args.base_path, f"DFQ3_udf_{spark.sparkContext.applicationId}")

    employees_df = spark.read.csv(employees_path, schema=EMPLOYEES_SCHEMA)
    # UDFs let us reuse custom Python logic, but they are usually slower and less optimizable
    # than built-in Spark expressions. That is why DFQ3.py is the preferred implementation.
    yearly_income_udf = udf(calculate_yearly_income, IntegerType())
    result_df = (
        # withColumn() adds a derived column to each row of the input DataFrame.
        employees_df.withColumn("yearly_income", yearly_income_udf(col("salary")))
        .select("name", "yearly_income")
        .orderBy(col("yearly_income").desc(), col("name"))
    )

    # collect() is safe because the dataset used in the lab is intentionally small.
    results = [(row.name, row.yearly_income) for row in result_df.collect()]
    for item in results:
        print(item)

    if output_path:
        if "://" in output_path:
            # overwrite keeps repeated submissions simple during experimentation.
            result_df.coalesce(1).write.mode("overwrite").csv(output_path)
        else:
            write_local_csv_output(output_path, results)
        print(f"Saved to: {output_path}")

    spark.stop()


if __name__ == "__main__":
    main()
```
<!-- END AUTO-CODE -->

## Appendix: Toy join using only RDD transformations

`RddQ4.py` does not use the same CSV files as the main lab. It is an in-memory toy example that demonstrates how join logic can be built using only RDD transformations.

<!-- AUTO-CODE: code/RddQ4.py -->
``` python
from pyspark.sql import SparkSession

# This file is a small join demo built from in-memory Python data.
# It is useful for understanding the mechanics of RDD joins before reading CSV files.

# Create the SparkContext.
sc = SparkSession \
    .builder \
    .appName("Join Datasets with RDD") \
    .getOrCreate() \
    .sparkContext

# MINIMIZE LOG OUTPUT
sc.setLogLevel("ERROR")

# --------------------------
# Initial data
# --------------------------

# Dataset A: (employee_id, employee_name, department_id)
data_a = [
    (1, "George K", 1),
    (2, "John T", 2),
    (3, "Mary M", 1),
    (4, "Jerry S", 3)
]

# Dataset B: (department_id, department_name)
data_b = [
    (1, "Dep A"),
    (2, "Dep B"),
    (3, "Dep C")
]

# --------------------------
# Create RDDs
# --------------------------

# parallelize() creates RDDs directly from Python collections that already exist in memory.
rdd_a = sc.parallelize(data_a)
rdd_b = sc.parallelize(data_b)

# --------------------------
# Prepare for join
# --------------------------

# Create key-value pairs using department_id as the key.
# The dataset tag tells us later whether a row came from the employee side or the department side.

# From Dataset A:
# (department_id, (1, (employee_id, employee_name, department_id)))
left = rdd_a.map(lambda x: (x[2], (1, x)))

# From Dataset B:
# (department_id, (2, (department_id, department_name)))
right = rdd_b.map(lambda x: (x[0], (2, x)))

# --------------------------
# Union the two RDDs
# --------------------------

# union() simply concatenates the two keyed datasets into one RDD.
unioned_data = left.union(right)

# --------------------------
# Group by department_id
# --------------------------

# groupByKey() brings together all rows that share the same department_id.
# This is a very explicit teaching approach for understanding joins, even if it is not the most efficient one.
grouped = unioned_data.groupByKey()

# --------------------------
# Function for merging the data
# --------------------------

def arrange(records):
    left_origin = []   # Records from Dataset A (employees)
    right_origin = []  # Records from Dataset B (departments)

    for (source_id, value) in records:
        if source_id == 1:
            left_origin.append(value)
        elif source_id == 2:
            right_origin.append(value)

    # Return every employee/department-name combination for one department id.
    return [(employee, dept) for employee in left_origin for dept in right_origin]

# --------------------------
# Final join result
# --------------------------

# flatMapValues() keeps the key and emits one output row for every join match.
# The final shape is similar to a join result produced by relational systems.
joined = grouped.flatMapValues(lambda x: arrange(x))

# collect() is safe here because the in-memory demo is tiny.
# Returns: (department_id, ((employee_id, name, dept_id), (dept_id, dept_name)))
for record in joined.collect():
    print(record)
```
<!-- END AUTO-CODE -->

## Main takeaways from this lab

- `Q1-Q3` now have a clean `RDD / DataFrame / SQL` matrix
- the names of the reference scripts now match the API the student is actually reading
- `DF2b.py` and `DFQ3_udf.py` are extras, not core comparisons
- `RddQ4.py` is an appendix, not a canonical `Q4`
