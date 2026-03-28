# Τοπική ανάπτυξη Spark με PyCharm

## Ρύθμιση του τοπικού περιβάλλοντος

Αυτός είναι ο εναλλακτικός οδηγός του βήματος `02` για τοπική ανάπτυξη Spark.

Αν θέλετε τη ροή που έχει δοκιμαστεί περισσότερο στο μάθημα, ακολουθήστε τον οδηγό [VS Code](../02_vscode-local-authoring/README.md). Αν όμως σας βολεύει περισσότερο το PyCharm, μπορείτε να ακολουθήσετε τον παρόντα οδηγό και μετά να συνεχίσετε κανονικά στον ίδιο ενιαίο οδηγό τοπικής εξάσκησης με Spark.

Μπορείτε να δείτε τον οδηγό προγραμματισμού του Apache Spark εδώ:

https://spark.apache.org/docs/latest/rdd-programming-guide.html

Ο παρακάτω οδηγός θεωρεί ότι έχετε εγκατεστημένο το **PyCharm Community Edition** και ότι η **Python 3.11** υπάρχει ήδη από το `01_workstation-setup`. Για το `pyspark`, η Python 3.11 είναι η προτεινόμενη βάση.

PyCharm Community Edition:

https://www.jetbrains.com/pycharm/download/

## Άνοιγμα του repository στο PyCharm

Ο οδηγός `02` υποστηρίζει δύο ισότιμες τοπικές διαδρομές:

- `Windows / PowerShell`
- `WSL / Ubuntu`

Αν ολοκληρώσατε ήδη το `01_workstation-setup`, το repository μπορεί να βρίσκεται:

- είτε σε φάκελο των Windows, π.χ. `C:\Users\<username>\bigdata-uth`
- είτε μέσα στο WSL, π.χ. `~/bigdata-uth`

Ανοίξτε το PyCharm και επιλέξτε να ανοίξετε το υπάρχον project directory `bigdata-uth`.

Για διαδρομή Windows, χρησιμοποιήστε το project των Windows και PowerShell terminal.
Για διαδρομή WSL, χρησιμοποιήστε το αντίστοιχο project μέσα από το WSL και WSL terminal.

![Εικόνα 1](images/img1.png)

Αν τελικά δημιουργήσετε νέο project από την αρχή, τότε:

- επιλέξτε project τύπου `Pure Python`
- δώστε ένα όνομα όπως `Spark_example`
- αποφύγετε κενά σε ονόματα αρχείων και καταλόγων
- στο `Interpreter type` επιλέξτε `Project venv`
- ως base interpreter επιλέξτε την Python 3.11
- η επιλογή `Create a welcome script` είναι προαιρετική

![Εικόνα 2](images/img3.png)

Αν το PyCharm εμφανίσει μήνυμα από το Microsoft Defender για exclusions φακέλων, μπορείτε να επιλέξετε `Exclude folders`. Δεν είναι υποχρεωτικό για να τρέξει το παράδειγμα, αλλά συνήθως βοηθάει στις επιδόσεις του IDE.

![Εικόνα 3](images/img2.png)

## Εγκατάσταση Python πακέτων

Αφού δημιουργηθεί το project, εγκαταστήστε τα πακέτα `pyspark` και `psutil` στο interpreter του project.

Μπορείτε να το κάνετε είτε:

- από το `Python Packages` tool window
- από το `Settings | Python | Interpreter`
- από το ενσωματωμένο terminal του PyCharm με:
  ```bash
  python -m pip install pyspark==3.5.8 psutil
  ```

Για αυτόν τον οδηγό δεν χρειάζεται να εγκαταστήσετε ξεχωριστά το Apache Spark στον υπολογιστή σας. Αρκούν το `pyspark` μέσα στο `.venv` και η Java.

## Έλεγχος Java

Για τοπική εκτέλεση PySpark, η γραμμή Spark 3.5.8 του μαθήματος δουλεύει κανονικά τόσο με `Java 17` στα Windows όσο και με `Java 11` στο WSL, σύμφωνα με το baseline του `01_workstation-setup`.

Έλεγχος από PowerShell ή WSL:

```text
java -version
```

Αν η εντολή δεν δουλεύει, επιστρέψτε πρώτα στον οδηγό `01_workstation-setup`.

## Δημιουργία αρχείων παραδείγματος

Αν ακολουθείτε τη ροή του αποθετηρίου, δεν χρειάζεται να δημιουργήσετε νέο `main.py` και νέο `text.txt`. Μπορείτε να χρησιμοποιήσετε τα βασικά αρχεία που υπάρχουν ήδη:

- `code/wordcount.py`
- `examples/text.txt`

Το παρακάτω scratch παράδειγμα παραμένει χρήσιμο μόνο αν θέλετε να δείτε το ελάχιστο δυνατό Spark script από το μηδέν.

Δημιουργήστε δύο αρχεία στον κατάλογο του project: `main.py` και `text.txt`.

Αν έχει δημιουργηθεί αυτόματα welcome script, μπορείτε απλώς να αντικαταστήσετε τα περιεχόμενά του με το παρακάτω `main.py`.

```python
import os
import sys

from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable


def main() -> None:
    spark = SparkSession.builder.appName("Word Count example").getOrCreate()
    sc = spark.sparkContext

    wordcount = (
        sc.textFile("text.txt")
        .flatMap(lambda line: line.split())
        .map(lambda word: (word, 1))
        .reduceByKey(lambda left, right: left + right)
        .sortBy(lambda item: item[1], ascending=False)
    )

    print(wordcount.collect())
    spark.stop()


if __name__ == "__main__":
    main()
```

Οι δύο γραμμές με το `sys.executable` λένε ρητά στο Spark να χρησιμοποιήσει τον ίδιο Python interpreter που έχει επιλέξει το project στο PyCharm. Έτσι, για αυτό το πρώτο παράδειγμα δεν χρειάζεται να δηλώσετε χειροκίνητα `PYSPARK_PYTHON` και `PYSPARK_DRIVER_PYTHON` στα Run Configurations.

Στο `text.txt` βάλτε ενδεικτικά:

```text
spark spark data
big data spark
python spark
```

## Εκτέλεση και debugging στο PyCharm

Ανοίξτε το `main.py` και εκτελέστε το πρόγραμμα με έναν από τους παρακάτω τρόπους:

- από το πράσινο εικονίδιο `Run` στο gutter
- με δεξί κλικ στο αρχείο και επιλογή `Run 'main'`
- με το shortcut `Shift+F10`

Για debugging:

- πατήστε το εικονίδιο `Debug` στο gutter
- ή κάντε δεξί κλικ και επιλέξτε `Debug 'main'`

Για αυτό το απλό παράδειγμα δεν χρειάζεται να δημιουργήσετε χειροκίνητα Run Configuration με environment variables. Το PyCharm μπορεί να δημιουργήσει αυτόματα ένα προσωρινό run/debug configuration για το τρέχον αρχείο, και αυτό είναι αρκετό.

Την πρώτη φορά που θα εκτελέσετε το πρόγραμμα, μπορεί να εμφανιστεί ερώτηση από το firewall / Windows Defender για το `OpenJDK Platform binary`. Αν εμφανιστεί, επιλέξτε `Allow`, ώστε το Spark να μπορέσει να ανοίξει την τοπική θύρα που χρειάζεται.

Αν όλα έχουν ρυθμιστεί σωστά, θα δείτε στο output αποτέλεσμα όπως:

```text
[('spark', 4), ('data', 2), ('big', 1), ('python', 1)]
```

## Πειραματισμός με `pyspark`

Αν θέλετε να πειραματίζεστε διαδραστικά με Spark, έχετε δύο πρακτικές επιλογές:

- το `pyspark`, που ανοίγει έτοιμη κονσόλα με διαθέσιμα τα `sc` και `spark`, αλλά σε Windows συχνά δεν δίνει βολικό history με τα πλήκτρα `Up` / `Down`
- την κανονική Python κονσόλα που ανοίγετε με `python`, η οποία συνήθως έχει πιο βολικό history και editing, αλλά θέλει χειροκίνητη δημιουργία του `SparkSession`

Σημείωση: το `pyspark` είναι για Python, ενώ το `spark-shell` είναι Scala shell. Η εντολή `sparkshell` χωρίς παύλα δεν είναι έγκυρη.

### Επιλογή 1: `pyspark`

Το `pyspark` είναι ο πιο γρήγορος τρόπος αν θέλετε να ξεκινήσετε αμέσως με έτοιμα τα `sc` και `spark`.

Αφού έχετε ενεργό το `.venv` και η εντολή `java -version` δουλεύει, εκτελέστε στο terminal.

Από PowerShell:

```powershell
$env:PYSPARK_PYTHON="$PWD\.venv\Scripts\python.exe"
$env:PYSPARK_DRIVER_PYTHON=$env:PYSPARK_PYTHON
pyspark
```

Από WSL:

```bash
export PYSPARK_PYTHON="$PWD/.venv/bin/python"
export PYSPARK_DRIVER_PYTHON="$PYSPARK_PYTHON"
pyspark
```

Μόλις ανοίξει το shell, μπορείτε να δοκιμάσετε για παράδειγμα:

```python
sc.parallelize([1, 2, 3]).count()
spark.range(5).show()
```

Για έξοδο από το shell:

```python
exit()
```

### Επιλογή 2: άνοιγμα κανονικής Python κονσόλας από το terminal

Αν θέλετε πιο άνετο history και πιο προβλέψιμη εμπειρία στο terminal, μπορείτε να ανοίξετε πρώτα την κανονική Python κονσόλα:

```bash
python
```

και στη συνέχεια να δημιουργήσετε χειροκίνητα το Spark session:

```python
import os
import sys
from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

spark = SparkSession.builder.appName("playground").getOrCreate()
sc = spark.sparkContext
```

Μετά μπορείτε να πειραματιστείτε με εντολές όπως:

```python
sc.parallelize([1, 2, 3]).count()
spark.range(5).show()
```

Όταν τελειώσετε:

```python
spark.stop()
exit()
```

## Έλεγχος του Spark UI

Όσο το πρόγραμμα εκτελείται, μπορείτε να παρακολουθείτε το Spark UI συνήθως στο:

[http://localhost:4040](http://localhost:4040)

Μόλις τερματίσετε την εκτέλεση του προγράμματος, σταματά και ο αντίστοιχος web server του Spark UI.

## Επόμενος τοπικός οδηγός

Αφού ολοκληρώσετε αυτόν τον βασικό οδηγό, η προτεινόμενη συνέχεια είναι ο ενιαίος οδηγός τοπικής εξάσκησης με Spark:

- [../03_local-spark-workbook/README.md](../03_local-spark-workbook/README.md)

Η ακριβής εμφάνιση του Spark UI μπορεί να διαφέρει λίγο ανάλογα με την έκδοση του Spark, αλλά η βασική ιδέα παραμένει η ίδια.

![Εικόνα 4](images/img13.png)

## Χρήσιμες παρατηρήσεις

- Αν το `java -version` δεν δουλεύει, κλείστε και ανοίξτε ξανά το PyCharm και δημιουργήστε νέο terminal. Αν συνεχίσει να μην δουλεύει, επιστρέψτε στον οδηγό `01_workstation-setup`.
- Αν το project δεν χρησιμοποιεί το σωστό `.venv`, ελέγξτε ξανά το `Settings | Python | Interpreter`.
- Αν δείτε warnings για `winutils.exe` ή `NativeCodeLoader`, μπορείτε να τα αγνοήσετε σε αυτό το απλό τοπικό παράδειγμα σε Windows.
- Αν το αρχείο `text.txt` δεν βρίσκεται στον σωστό κατάλογο, το πρόγραμμα θα αποτύχει επειδή δεν θα το βρει.
- Αν η πόρτα `4040` χρησιμοποιείται ήδη, το Spark μπορεί να ξεκινήσει το UI σε άλλη θύρα όπως `4041`.
- Το `Python Console` του PyCharm είναι χρήσιμο για πιο προχωρημένη διαδραστική χρήση, αλλά δεν χρειάζεται για αυτό το πρώτο παράδειγμα.
- Αν αργότερα περάσετε στον οδηγό `04`, η απομακρυσμένη εκτέλεση δεν γίνεται από PowerShell αλλά μόνο από WSL.
