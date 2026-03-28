# Τοπική εξάσκηση με Spark: RDD, DataFrame API και Spark SQL

Αυτός είναι ο βασικός τοπικός οδηγός εξάσκησης του μαθήματος.

Ακολουθεί τον οδηγό ρύθμισης σε [VS Code](../02_vscode-local-authoring/README.md) ή [PyCharm](../02_pycharm-local-authoring/README.md) και προηγείται του οδηγού [απομακρυσμένης εκτέλεσης σε Kubernetes](../04_remote-spark-kubernetes/README.md).

Η παιδαγωγική του λογική είναι:

- πρώτα μαθαίνεις το Spark API τοπικά
- μετά αλλάζεις περιβάλλον εκτέλεσης
- δεν αλλάζεις ταυτόχρονα και API και υποδομή

## Τι υποθέτουμε

Ο οδηγός υποθέτει ότι:

- έχεις ήδη ολοκληρώσει έναν από τους τοπικούς οδηγούς ρύθμισης
- έχεις ήδη το κλωνοποιημένο αποθετήριο είτε σε φάκελο των Windows είτε μέσα στο WSL
- το `.venv` είναι έτοιμο
- το `java -version` δουλεύει
- τρέχεις από τη ρίζα του repository `bigdata-uth`

Πριν τρέξεις τα examples, άνοιξε terminal μέσα στο repo και ενεργοποίησε το virtual environment.

Από PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Από WSL:

```bash
cd ~/bigdata-uth
source .venv/bin/activate
```

## Η προτεινόμενη τοπική διαδρομή

1. `RDD fundamentals` με μικρά σύνολα δεδομένων και απλές μετασχηματίσεις
2. `DataFrame API` πάνω στα `employees.csv` και `departments.csv`
3. `Spark SQL` πάνω στα ίδια ακριβώς ερωτήματα
4. μετάβαση στην απομακρυσμένη εκτέλεση χωρίς αλλαγή του ερωτήματος

## Τα datasets

| Dataset | Χρήση |
| --- | --- |
| `examples/text.txt` | τοπικό wordcount |
| `examples/club_python.txt` | πράξεις συνόλων με RDD |
| `examples/club_robotics.txt` | πράξεις συνόλων με RDD |
| `examples/sales.csv` | φιλτράρισμα, ταξινόμηση, joins |
| `examples/products.csv` | joins και ομαδοποιήσεις ανά κατηγορία |
| `examples/scores.csv` | μέσος όρος ανά μάθημα |
| `examples/employees.csv` | Q1-Q3 τοπικά και απομακρυσμένα |
| `examples/departments.csv` | Q1-Q3 τοπικά και απομακρυσμένα |

## Μέρος Α: Βασικές έννοιες RDD

Τα βασικά τοπικά RDD scripts βρίσκονται στο [`code/local/rdd`](../../code/local/rdd).

| Παράδειγμα | Script | Δεδομένα | Τι δείχνει |
| --- | --- | --- | --- |
| 1 | `code/local/rdd/01_parallelize_basics.py` | λίστα Python | `parallelize`, `filter`, `map`, `sortBy`, `reduce` |
| 2 | `code/local/rdd/02_textfile_wordcount.py` | `examples/text.txt` | `textFile`, `flatMap`, `reduceByKey` |
| 3 | `code/local/rdd/03_club_members.py` | `examples/club_python.txt`, `examples/club_robotics.txt` | union, intersection, distinct |
| 4 | `code/local/rdd/04_products_by_category.py` | `examples/products.csv` | διαμόρφωση key-value και `groupByKey` |
| 5 | `code/local/rdd/05_sales_filter_sort.py` | `examples/sales.csv` | ανάγνωση CSV, filter, sort |
| 6 | `code/local/rdd/06_join_sales_products.py` | `examples/sales.csv`, `examples/products.csv` | join και έσοδα ανά κατηγορία |
| 7 | `code/local/rdd/07_scores_aggregatebykey.py` | `examples/scores.csv` | `aggregateByKey` |

### Ενδεικτικό παράδειγμα RDD

Το πρώτο script αρκεί για να δει ο φοιτητής τη βασική μορφή ενός τοπικού Spark job:

<!-- AUTO-CODE: code/local/rdd/01_parallelize_basics.py -->
``` python
import os
import sys

from pyspark.sql import SparkSession

# Keep the Python executable consistent between the driver and Spark tasks.
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = (
        # local[*] uses all local CPU cores and is the simplest setup for practice.
        SparkSession.builder.master("local[*]")
        .config("spark.submit.deployMode", "client")
        .appName("parallelize-basics")
        .getOrCreate()
    )
    # The SparkSession is the main entry point; from it we access the SparkContext for RDD work.
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    # parallelize() creates an RDD directly from data that already exists in Python memory.
    numbers = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4)

    # filter() keeps only the records that satisfy the predicate.
    even_numbers = numbers.filter(lambda x: x % 2 == 0)

    # map() transforms each input record into exactly one output record.
    squared_numbers = even_numbers.map(lambda x: (x, x * x))

    sorted_numbers = squared_numbers.sortBy(
        lambda item: item[1],
        ascending=False,
    )  # Sorting is another transformation, so nothing runs yet.

    # reduce() is an action: it triggers execution and combines all elements into one value.
    total_sum = numbers.reduce(lambda left, right: left + right)

    # getNumPartitions() helps students connect the logical RDD with Spark's parallel execution units.
    print("Partitions:", numbers.getNumPartitions())
    # collect() is acceptable here because the result is tiny.
    print("Even squares:", sorted_numbers.collect())
    print("Sum:", total_sum)

    spark.stop()


if __name__ == "__main__":
    main()
```
<!-- END AUTO-CODE -->

Εκτέλεση:

```bash
python code/local/rdd/01_parallelize_basics.py
```

Για τα υπόλοιπα παραδείγματα RDD, η μορφή εκτέλεσης είναι η ίδια:

```bash
python code/local/rdd/<script>.py
```

## Μέρος Β: Δεδομένα σε μορφή πινάκων με DataFrame API και Spark SQL

Τα βασικά ερωτήματα σε μορφή πινάκων είναι τα ίδια ακριβώς που θα τρέξουν αργότερα και απομακρυσμένα.

| Ερώτημα | DataFrame API | Spark SQL | Dataset |
| --- | --- | --- | --- |
| Q1: 5 χαμηλότεροι μισθοί | `code/DFQ1.py` | `code/SQLQ1.py` | `employees.csv` |
| Q2: 3 πιο καλοπληρωμένοι του `Dep A` | `code/DFQ2.py` | `code/SQLQ2.py` | `employees.csv`, `departments.csv` |
| Q3: ετήσιο εισόδημα | `code/DFQ3.py` | `code/SQLQ3.py` | `employees.csv` |

Extras:

- `code/DF2b.py`: άθροισμα μισθών ανά τμήμα
- `code/DFQ3_udf.py`: annual income με UDF για comparison

### Ενδεικτικό παράδειγμα με DataFrame API

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

Εκτέλεση:

```bash
python code/DFQ1.py
```

### Ενδεικτικό παράδειγμα με Spark SQL

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

Εκτέλεση:

```bash
python code/SQLQ1.py
```

Για τα υπόλοιπα παραδείγματα:

```bash
python code/DFQ2.py
python code/SQLQ2.py
python code/DFQ3.py
python code/SQLQ3.py
python code/DF2b.py
python code/DFQ3_udf.py
```

## Από την τοπική στην απομακρυσμένη εκτέλεση

Αυτός ο οδηγός υπάρχει για να σταθεροποιήσει τρία πράγματα πριν περάσετε στο Kubernetes:

- ποιο είναι το ερώτημα
- ποιο είναι το βασικό script
- ποιο είναι το αναμενόμενο αποτέλεσμα

Στην απομακρυσμένη εκτέλεση αλλάζουν μόνο:

- τα paths εισόδου και εξόδου
- ο τρόπος submit
- ο τρόπος παρακολούθησης

Σημαντικό: οι οδηγοί `04` και `05` εκτελούνται μόνο από WSL.

Αν μέχρι εδώ δουλέψατε απευθείας από τα Windows, πριν περάσετε στον απομακρυσμένο οδηγό ανοίξτε το κλωνοποιημένο αποθετήριο στο WSL, π.χ. `~/bigdata-uth`.

Από εκεί και πέρα, βγείτε από το local `.venv` ώστε το επόμενο `spark-submit` να είναι αυτό της εγκατάστασης Spark στο WSL και όχι το wrapper του `pyspark` μέσα στο virtual environment:

```bash
deactivate 2>/dev/null || true
source ~/bigdata-env.sh
hash -r
command -v spark-submit
```

Ο επόμενος οδηγός είναι ο [οδηγός απομακρυσμένης εκτέλεσης Spark σε Kubernetes](../04_remote-spark-kubernetes/README.md).
