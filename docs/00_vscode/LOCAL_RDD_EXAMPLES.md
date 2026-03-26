# Τοπικά παραδείγματα με το απλό RDD API στο VS Code

Αυτός ο οδηγός συμπληρώνει το [README.md](README.md) του VS Code και δίνει μικρά, τοπικά, φιλικά για αρχάριους παραδείγματα με το απλό RDD API του Spark.

Οι ιδέες των παραδειγμάτων βασίζονται:

- στο επίσημο **Spark RDD Programming Guide**
- στο επίσημο **PySpark API Reference**

Χρήσιμοι σύνδεσμοι:

- https://spark.apache.org/docs/latest/rdd-programming-guide.html
- https://spark.apache.org/docs/latest/api/python/reference/pyspark.html

## Τι υποθέτουμε

Ο οδηγός υποθέτει ότι:

- έχεις ήδη ακολουθήσει το [README.md](README.md)
- το `.venv` του project είναι έτοιμο
- το `java -version` δουλεύει
- τρέχεις τις εντολές από τη ρίζα του repository `bigdata-uth`

## Τα σύνολα δεδομένων που θα χρησιμοποιήσουμε

Για τα παρακάτω παραδείγματα υπάρχουν μικρά τοπικά σύνολα δεδομένων μέσα στο `examples`:

- `examples/text.txt`
- `examples/club_python.txt`
- `examples/club_robotics.txt`
- `examples/sales.csv`
- `examples/products.csv`
- `examples/scores.csv`

## Τα έτοιμα αρχεία

Υπάρχουν ήδη έτοιμα εκτελέσιμα αρχεία στον φάκελο `local_demos`.

```powershell
Get-ChildItem .\local_demos
```

## Τι θα δείξουμε

Κάθε παράδειγμα απαντά ένα μικρό, συγκεκριμένο ερώτημα:

1. Πώς φτιάχνω RDD από λίστα και κάνω βασικούς μετασχηματισμούς;
2. Πώς μετράω λέξεις από ένα απλό αρχείο κειμένου;
3. Πώς βρίσκω μαθητές που είναι σε μία ή και στις δύο ομάδες;
4. Πώς ομαδοποιώ προϊόντα ανά κατηγορία;
5. Πώς φιλτράρω και ταξινομώ πωλήσεις από CSV;
6. Πώς ενώνω δύο σύνολα δεδομένων και υπολογίζω έσοδα ανά κατηγορία;
7. Πώς υπολογίζω μέσο όρο βαθμών ανά μάθημα;

## Παράδειγμα 1: Κράτα τους άρτιους αριθμούς και βρες τα τετράγωνά τους

**Τι θέλουμε να υπολογίσουμε**

Θέλουμε να ξεκινήσουμε από τους αριθμούς `1` έως `10`, να κρατήσουμε μόνο τους άρτιους, να υπολογίσουμε το τετράγωνό τους και να τους εμφανίσουμε από τον μεγαλύτερο προς τον μικρότερο.

Έτοιμο αρχείο: `local_demos/01_parallelize_basics.py`

```python
import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("parallelize-basics").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    numbers = sc.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 4)  # Create a small RDD from a Python list.

    even_numbers = numbers.filter(lambda x: x % 2 == 0)  # Keep only the even numbers.

    squared_numbers = even_numbers.map(lambda x: (x, x * x))  # Turn each number into (number, square).

    sorted_numbers = squared_numbers.sortBy(
        lambda item: item[1],
        ascending=False,
    )  # Sort by the square value from largest to smallest.

    total_sum = numbers.reduce(lambda left, right: left + right)  # Add all numbers in the original RDD.

    print("Partitions:", numbers.getNumPartitions())
    print("Even squares:", sorted_numbers.collect())
    print("Sum:", total_sum)

    spark.stop()


if __name__ == "__main__":
    main()
```

Εκτέλεση:

```powershell
.\.venv\Scripts\python.exe .\local_demos\01_parallelize_basics.py
```

Αναμενόμενο αποτέλεσμα:

```text
Partitions: 4
Even squares: [(10, 100), (8, 64), (6, 36), (4, 16), (2, 4)]
Sum: 55
```

Τι δείχνει:

- `parallelize`
- `filter`
- `map`
- `sortBy`
- `reduce`

## Παράδειγμα 2: Μέτρησε πόσες φορές εμφανίζεται κάθε λέξη

**Τι θέλουμε να υπολογίσουμε**

Θέλουμε να διαβάσουμε το αρχείο `examples/text.txt` και να μετρήσουμε πόσες φορές εμφανίζεται κάθε λέξη.

Το αρχείο είναι εσκεμμένα απλό, ώστε να μη χρειαστούμε `regex` ή άλλο πιο σύνθετο preprocessing.

Έτοιμο αρχείο: `local_demos/02_textfile_wordcount.py`

```python
import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("textfile-wordcount").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    lines = sc.textFile("examples/text.txt")  # Read the input file line by line.

    words = lines.flatMap(lambda line: line.split())  # Split each line into separate words.

    word_pairs = words.map(lambda word: (word, 1))  # Turn each word into (word, 1).

    word_counts = word_pairs.reduceByKey(lambda left, right: left + right)  # Add the counts for the same word.

    sorted_word_counts = word_counts.sortBy(lambda item: (-item[1], item[0]))  # Show the most frequent words first.

    for item in sorted_word_counts.collect():
        print(item)

    spark.stop()


if __name__ == "__main__":
    main()
```

Εκτέλεση:

```powershell
.\.venv\Scripts\python.exe .\local_demos\02_textfile_wordcount.py
```

Αναμενόμενο αποτέλεσμα:

```text
('spark', 4)
('data', 2)
('big', 1)
('python', 1)
```

Τι δείχνει:

- `textFile`
- `flatMap`
- `map`
- `reduceByKey`

## Παράδειγμα 3: Βρες ποιοι μαθητές είναι σε μία ή και στις δύο ομάδες

**Τι θέλουμε να υπολογίσουμε**

Έχουμε δύο λίστες μαθητών:

- αυτούς που δήλωσαν το `Python club`
- αυτούς που δήλωσαν το `Robotics club`

Θέλουμε:

1. να βρούμε όλους τους μαθητές που εμφανίζονται σε τουλάχιστον μία ομάδα
2. να βρούμε ποιοι μαθητές εμφανίζονται και στις δύο ομάδες

Έτοιμο αρχείο: `local_demos/03_club_members.py`

```python
import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("club-members").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    python_club = sc.textFile("examples/club_python.txt")  # Read the first club list.
    robotics_club = sc.textFile("examples/club_robotics.txt")  # Read the second club list.

    all_students = python_club.union(robotics_club)  # Combine the two club lists into one RDD.

    unique_students = all_students.distinct().sortBy(lambda name: name)  # Keep each student only once.

    common_students = python_club.intersection(robotics_club).sortBy(
        lambda name: name
    )  # Keep only students who appear in both lists.

    print("Students in at least one club:", unique_students.collect())
    print("Students in both clubs:", common_students.collect())

    spark.stop()


if __name__ == "__main__":
    main()
```

Εκτέλεση:

```powershell
.\.venv\Scripts\python.exe .\local_demos\03_club_members.py
```

Αναμενόμενο αποτέλεσμα:

```text
Students in at least one club: ['Alice', 'Bob', 'Christina', 'Dimitris', 'Eleni', 'George']
Students in both clubs: ['Bob', 'Eleni']
```

Τι δείχνει:

- `union`
- `distinct`
- `intersection`

## Παράδειγμα 4: Δείξε ποια προϊόντα ανήκουν σε κάθε κατηγορία

**Τι θέλουμε να υπολογίσουμε**

Θέλουμε να διαβάσουμε το `examples/products.csv` και να δούμε ποια προϊόντα ανήκουν σε κάθε κατηγορία.

Έτοιμο αρχείο: `local_demos/04_products_by_category.py`

```python
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
```

Εκτέλεση:

```powershell
.\.venv\Scripts\python.exe .\local_demos\04_products_by_category.py
```

Αναμενόμενο αποτέλεσμα:

```text
[('Beverages', ['Coffee']), ('Electronics', ['Keyboard', 'Mouse']), ('Stationery', ['Markers', 'Notebook'])]
```

Τι δείχνει:

- `textFile`
- `map`
- `groupByKey`
- `mapValues`

## Παράδειγμα 5: Βρες τις πωλήσεις με συνολική αξία τουλάχιστον 20

**Τι θέλουμε να υπολογίσουμε**

Θέλουμε να διαβάσουμε τις πωλήσεις από το `examples/sales.csv`, να υπολογίσουμε τη συνολική αξία κάθε πώλησης και να εμφανίσουμε μόνο όσες έχουν αξία τουλάχιστον `20`.

Έτοιμο αρχείο: `local_demos/05_sales_filter_sort.py`

```python
import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("sales-filter-sort").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    rows = sc.textFile("examples/sales.csv").map(lambda line: line.split(","))  # Split each CSV line into columns.

    sales = rows.map(
        lambda row: (
            row[0],
            row[1],
            int(row[2]),
            float(row[3]),
            row[4],
            int(row[2]) * float(row[3]),
        )
    )  # Build (sale_id, product_id, quantity, unit_price, city, total_value).

    high_value_sales = sales.filter(lambda row: row[5] >= 20.0)  # Keep only sales with total value at least 20.

    selected_columns = high_value_sales.map(
        lambda row: (row[0], row[1], row[4], row[5])
    )  # Keep only the columns we want to display.

    sorted_sales = selected_columns.sortBy(lambda row: (-row[3], row[0]))  # Show the highest-value sales first.

    for item in sorted_sales.collect():
        print(item)

    spark.stop()


if __name__ == "__main__":
    main()
```

Εκτέλεση:

```powershell
.\.venv\Scripts\python.exe .\local_demos\05_sales_filter_sort.py
```

Αναμενόμενο αποτέλεσμα:

```text
('S005', 'P4', 'Patras', 50.0)
('S006', 'P2', 'Volos', 36.0)
('S008', 'P4', 'Volos', 25.0)
('S004', 'P3', 'Volos', 24.0)
```

Τι δείχνει:

- `textFile`
- `map`
- `filter`
- `sortBy`

## Παράδειγμα 6: Υπολόγισε συνολικά έσοδα ανά κατηγορία προϊόντων

**Τι θέλουμε να υπολογίσουμε**

Έχουμε:

- τις πωλήσεις στο `examples/sales.csv`
- τα προϊόντα και την κατηγορία τους στο `examples/products.csv`

Θέλουμε να ενώσουμε τα δύο datasets και να υπολογίσουμε τα συνολικά έσοδα ανά κατηγορία προϊόντων.

Επειδή σε αυτό το στάδιο θέλουμε να αποφύγουμε τα Hadoop filesystem APIs σε Windows, το τελικό αποτέλεσμα θα αποθηκευτεί με απλή εγγραφή αρχείου μέσω Python σε ένα τοπικό αρχείο.

Έτοιμο αρχείο: `local_demos/06_join_sales_products.py`

```python
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
```

Εκτέλεση:

```powershell
.\.venv\Scripts\python.exe .\local_demos\06_join_sales_products.py
```

Αναμενόμενο αποτέλεσμα:

```text
('Electronics', 129.0)
('Stationery', 37.0)
('Beverages', 36.0)
Saved to: output/category_revenue_local.txt
```

Μετά την εκτέλεση θα δημιουργηθεί και το αρχείο:

```text
output/category_revenue_local.txt
```

Τι δείχνει:

- `join`
- `map`
- `reduceByKey`
- απλή τοπική εγγραφή αρχείου με Python

## Παράδειγμα 7: Υπολόγισε τον μέσο όρο βαθμών ανά μάθημα

**Τι θέλουμε να υπολογίσουμε**

Θέλουμε να διαβάσουμε βαθμούς από το `examples/scores.csv` και να υπολογίσουμε τον μέσο όρο βαθμών για κάθε μάθημα.

Έτοιμο αρχείο: `local_demos/07_scores_aggregatebykey.py`

```python
import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("scores-aggregatebykey").getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    score_rows = sc.textFile("examples/scores.csv").map(
        lambda line: line.split(",")
    )  # Split each CSV line into columns.

    scores_by_course = score_rows.map(lambda row: (row[1], int(row[2])))  # Turn each row into (course, score).

    sums_and_counts = scores_by_course.aggregateByKey(
        (0, 0),
        lambda acc, score: (acc[0] + score, acc[1] + 1),
        lambda left, right: (left[0] + right[0], left[1] + right[1]),
    )  # Keep track of (sum_of_scores, number_of_scores) for each course.

    averages = sums_and_counts.mapValues(
        lambda item: round(item[0] / item[1], 2)
    )  # Turn each (sum, count) pair into an average.

    sorted_averages = averages.sortBy(
        lambda item: (-item[1], item[0])
    )  # Show the highest average first.

    for item in sorted_averages.collect():
        print(item)

    spark.stop()


if __name__ == "__main__":
    main()
```

Εκτέλεση:

```powershell
.\.venv\Scripts\python.exe .\local_demos\07_scores_aggregatebykey.py
```

Αναμενόμενο αποτέλεσμα:

```text
('Spark', 8.33)
('Databases', 7.75)
('Python', 7.67)
```

Τι δείχνει:

- `aggregateByKey`
- `mapValues`
- `sortBy`

## Προτεινόμενη σειρά για live demo

Για μια καθαρή παρουσίαση, φιλική προς αρχάριους, η πιο πρακτική σειρά είναι:

1. `01_parallelize_basics.py`
2. `02_textfile_wordcount.py`
3. `03_club_members.py`
4. `05_sales_filter_sort.py`
5. `06_join_sales_products.py`
6. `07_scores_aggregatebykey.py`
7. `04_products_by_category.py` ως bonus

## Χρήσιμες παρατηρήσεις

- Τρέχε τα scripts από τη ρίζα του repository.
- Για μικρά παραδείγματα το `collect()` είναι αποδεκτό.
- Η `countByValue()` και το `takeOrdered()` τα αφήνουμε εκτός αυτού του οδηγού για να παραμείνει το υλικό πιο συγκεντρωμένο.
- Αν θέλεις απλό τοπικό γράψιμο αρχείου σε αυτό το στάδιο, προτίμησε Python `open()` / `write()` πάνω σε μικρό αποτέλεσμα που έχει ήδη επιστρέψει στον driver.
- Αν θέλεις να βλέπεις τα jobs, άνοιξε το Spark UI στο `http://localhost:4040`.

## Επόμενα βήματα

Αν θέλεις να επεκτείνεις μόνος σου τα παραδείγματα, καλά επόμενα βήματα είναι:

- `takeOrdered`
- `countByValue`
- `sample`
- `countByKey`
- `cache`
