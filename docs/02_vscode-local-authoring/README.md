# Τοπική ανάπτυξη Spark με VS Code

## Ρύθμιση του τοπικού περιβάλλοντος

Μπορείτε να δείτε οδηγίες υλοποίησης με Apache Spark εδώ:

https://spark.apache.org/docs/latest/rdd-programming-guide.html

Ο παρών οδηγός θεωρεί ότι υπάρχει ήδη εγκατεστημένο στον υπολογιστή σας το **Visual Studio Code**.

Αυτή είναι η προτεινόμενη και δοκιμασμένη ροή του μαθήματος για τοπική ανάπτυξη. Αν προτιμάτε άλλο IDE, υπάρχει και ο εναλλακτικός οδηγός [PyCharm](../02_pycharm-local-authoring/README.md), αλλά η βασική διαδρομή που ελέγχεται συστηματικά στο μάθημα είναι το VS Code.

https://code.visualstudio.com/

Ο παρών οδηγός υποθέτει ότι η **Python 3.11** έχει ήδη εγκατασταθεί από το `01_workstation-setup`. Στο μάθημα χρησιμοποιούμε απλό τοπικό περιβάλλον με `venv`, οπότε η Python 3.11 είναι η προτεινόμενη βάση.

Για την Python στο VS Code θα χρειαστείτε τουλάχιστον τα παρακάτω extensions:

- `Python`
- `Pylance`
- προαιρετικά `Jupyter`

![Εικόνα 1](images/01_vscodeextensions.png)



## Άνοιγμα του repository

Ο οδηγός `02` υποστηρίζει δύο ισότιμες τοπικές διαδρομές:

- `Windows / PowerShell`
- `WSL / Ubuntu`

Αν ολοκληρώσατε ήδη το `01_workstation-setup`, μπορείτε να έχετε το repository:

- είτε σε φάκελο των Windows, π.χ. `C:\Users\<username>\bigdata-uth`
- είτε μέσα στο WSL, π.χ. `~/bigdata-uth`

Στο VS Code ανοίξτε τον φάκελο που αντιστοιχεί στη διαδρομή που διαλέξατε:

- για διαδρομή Windows, ανοίξτε τον κανονικό φάκελο των Windows και χρησιμοποιήστε PowerShell terminal
- για διαδρομή WSL, ανοίξτε το repo μέσω WSL integration και χρησιμοποιήστε WSL terminal

Σε αυτόν τον οδηγό, κάθε σημείο που διαφέρει θα δίνεται και για τα δύο περιβάλλοντα.


Κατά την πρώτη εκτέλεση του VS Code, αν σας ζητηθεί να εμπιστευθείτε τον φάκελο εργασίας σας, επιλέξτε `Yes, I trust the authors`.

![Εικόνα 2](images/02_trustauthors.png)




## Δημιουργία virtual environment στο VS Code

Ένα **virtual environment** είναι ένας απομονωμένος χώρος Python για ένα συγκεκριμένο project.  
Μέσα σε αυτόν τον χώρο εγκαθιστάτε τα πακέτα που χρειάζεται μόνο η συγκεκριμένη εργασία, χωρίς να επηρεάζετε τον υπόλοιπο υπολογιστή σας ή άλλα projects.

Στην πράξη, αυτό προσφέρει τρία βασικά πλεονεκτήματα:

- κρατά ξεχωριστές τις εξαρτήσεις κάθε εργασίας
- αποφεύγει συγκρούσεις ανάμεσα σε διαφορετικές εκδόσεις πακέτων
- κάνει πιο προβλέψιμο το run/debug περιβάλλον στο VS Code

Για το μάθημα προτείνεται να χρησιμοποιείτε **τοπικό virtual environment με `venv`** μέσα σε κάθε project. Αυτός είναι ο πιο καθαρός και πρακτικός τρόπος, γιατί:

- κάθε εργασία έχει τα δικά της πακέτα,
- αποφεύγονται συγκρούσεις μεταξύ διαφορετικών projects,
- το VS Code συνήθως εντοπίζει αυτόματα το `.venv` του project.

Ανοίξτε τον φάκελο `bigdata-uth` στο VS Code.


Ανοίξτε ένα terminal μέσα από το VS Code (`Terminal -> New Terminal`) και δημιουργήστε το virtual environment.

Από PowerShell:

```powershell
py -3.11 -m venv .venv
```

Από WSL:

```bash
python3 -m venv .venv
```

Η παραπάνω εντολή θα δημιουργήσει έναν κατάλογο `.venv` μέσα στο project σας.

## Ενεργοποίηση του virtual environment

Μετά τη δημιουργία του `.venv`, έχετε δύο απλούς τρόπους:

### Τρόπος 1: Κλείνω και ξανανοίγω το terminal

Συνήθως αρκεί να κλείσετε το terminal και να ανοίξετε νέο terminal μέσα στο VS Code.  
Το VS Code συνήθως εντοπίζει αυτόματα το `.venv` και το ενεργοποιεί μόνο του.

### Τρόπος 2: Χειροκίνητη ενεργοποίηση

Αν θέλετε, μπορείτε να το ενεργοποιήσετε και μόνοι σας.

Από PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Αν το PowerShell μπλοκάρει τα local scripts του virtual environment, τρέξτε πρώτα:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.venv\Scripts\Activate.ps1
```

Από WSL:

```bash
source .venv/bin/activate
```

Αν όλα έχουν πάει σωστά, θα δείτε συνήθως το `(.venv)` στην αρχή της γραμμής του terminal.

![Εικόνα 3](images/03_autovenvactivation.png)


## Εγκατάσταση πακέτων

Αφού ενεργοποιηθεί το virtual environment, εγκαταστήστε τα απαραίτητα πακέτα με:

```bash
python -m pip install pyspark==3.5.8 psutil
```

Μπορείτε να δείτε τα εγκατεστημένα πακέτα με:

```bash
python -m pip list
```

Προτιμούμε τη μορφή `python -m pip` αντί για σκέτο `pip`, γιατί έτσι είναι πιο σαφές ότι η εγκατάσταση γίνεται για τον Python interpreter που χρησιμοποιεί το project.

![Εικόνα 4](images/04_pysparkinstalled.png)


## Αν το terminal δεν ενεργοποιεί μόνο του το `.venv`

Από PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Από WSL:

```bash
source .venv/bin/activate
```

## Αν η δημιουργία του `.venv` κολλήσει

Σε ορισμένους υπολογιστές, η δημιουργία του `.venv` μπορεί να καθυστερήσει ή να κολλήσει στο βήμα όπου εγκαθίσταται το `pip`.

Από PowerShell:

```powershell
py -3.11 -m venv --without-pip .venv
.venv\Scripts\python.exe -m ensurepip --upgrade
```

Από WSL:

```bash
python3 -m venv --without-pip .venv
.venv/bin/python -m ensurepip --upgrade
```

Με αυτόν τον τρόπο, δημιουργείται πρώτα το virtual environment και στη συνέχεια εγκαθίσταται το `pip` σε δεύτερο βήμα.

## Τι να θυμάστε

Για το συγκεκριμένο μάθημα, η προτεινόμενη ροή είναι η εξής:

1. δημιουργώ το `.venv`
2. επιλέγω `Python: Select Interpreter`
3. εγκαθιστώ πακέτα με `python -m pip`
4. τρέχω ή κάνω debug από το VS Code

Η χειροκίνητη ενεργοποίηση είναι προαιρετική και χρησιμοποιείται κυρίως όταν δουλεύετε άμεσα από terminal.

## Έλεγχος Java

Για τοπική εκτέλεση PySpark, η γραμμή Spark 3.5.8 του μαθήματος δουλεύει κανονικά τόσο με `Java 17` στα Windows όσο και με `Java 11` στο WSL, σύμφωνα με το baseline του `01_workstation-setup`.
Δεν χρειάζεται να εγκαταστήσετε ξεχωριστά το Apache Spark στον υπολογιστή σας. Για αυτόν τον οδηγό αρκούν το `pyspark` μέσα στο `.venv` και η Java που εγκαταστάθηκε στο `01_workstation-setup`.

Έλεγχος από PowerShell ή WSL:

```text
java -version
```

Αν η εντολή δεν δουλεύει, επιστρέψτε πρώτα στον οδηγό `01_workstation-setup`.

## Δημιουργία αρχείων παραδείγματος

Αν ακολουθείτε τη ροή του αποθετηρίου, δεν χρειάζεται να δημιουργήσετε νέο `main.py` και νέο `text.txt`. Μπορείτε να χρησιμοποιήσετε τα βασικά αρχεία που υπάρχουν ήδη:

- `code/wordcount.py`
- `examples/text.txt`

Το παρακάτω μικρό αυτόνομο παράδειγμα παραμένει χρήσιμο μόνο αν θέλετε να δείτε το ελάχιστο δυνατό Spark script από το μηδέν.

Δημιουργήστε δύο αρχεία στον κατάλογο του project: `main.py` και `text.txt`.

Στο `main.py` βάλτε τον παρακάτω κώδικα:

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

Οι δύο γραμμές με το `sys.executable` λένε ρητά στο Spark να χρησιμοποιήσει τον ίδιο Python interpreter που έχει επιλέξει το project στο VS Code. Έτσι, για αυτό το πρώτο παράδειγμα δεν χρειάζεται ξεχωριστό `launch.json`.

Στο `text.txt` βάλτε ενδεικτικά:

```text
spark spark data
big data spark
python spark
```

## Εκτέλεση και debugging στο VS Code

Αφού έχετε ήδη επιλέξει τον interpreter από το `.venv`, ανοίξτε το `main.py` και εκτελέστε το πρόγραμμα με έναν από τους παρακάτω τρόπους:

- από το κουμπί `Run Python File`
- από το ενσωματωμένο terminal, με ενεργό το `.venv`, χρησιμοποιώντας `python main.py`

Για debugging:

- ανοίξτε το `Run and Debug`
- αν το VS Code σας ζητήσει τύπο ρύθμισης, επιλέξτε `Python Debugger: Current File`
- στη συνέχεια πατήστε `F5`

Για το συγκεκριμένο απλό παράδειγμα, αυτό αρκεί. Δεν χρειάζεται να γράψετε χειροκίνητα `launch.json`. Αν το VS Code δημιουργήσει αυτόματα ένα απλό `launch.json` στο πρώτο debug, μπορείτε να κρατήσετε την προεπιλεγμένη ρύθμιση.

Την πρώτη φορά που θα εκτελέσετε το πρόγραμμα, μπορεί να εμφανιστεί ερώτηση από το firewall / Windows Defender για το `OpenJDK Platform binary`. Αν εμφανιστεί, επιλέξτε `Allow`, ώστε το Spark να μπορέσει να ανοίξει την τοπική θύρα που χρειάζεται.

![Εικόνα 5](images/05_java_firewall.png)

Αν όλα έχουν ρυθμιστεί σωστά, θα δείτε στο terminal αποτέλεσμα όπως:

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

Ένας ακόμη τρόπος να παρακολουθείτε τι γίνεται είναι μέσω του URL στο οποίο τρέχει το Spark UI. Συνήθως, κατά την τοπική εκτέλεση, αυτό εμφανίζεται στο:

[http://localhost:4040](http://localhost:4040)

Μόλις τερματίσετε την εκτέλεση του προγράμματος, σταματά και ο αντίστοιχος web server του Spark UI.

Η ακριβής εμφάνιση του Spark UI μπορεί να διαφέρει λίγο ανάλογα με την έκδοση του Spark, αλλά η βασική ιδέα παραμένει η ίδια.

![Εικόνα 6](images/06_spark_ui.png)

## Επόμενος τοπικός οδηγός

Αφού ολοκληρώσετε αυτόν τον βασικό οδηγό, η προτεινόμενη συνέχεια είναι ο ενιαίος οδηγός τοπικής εξάσκησης με Spark:

- [../03_local-spark-workbook/README.md](../03_local-spark-workbook/README.md)

Εκεί βρίσκονται πλέον μαζί:

- τα μικρά τοπικά παραδείγματα με το RDD API
- τα τοπικά παραδείγματα με DataFrames και Spark SQL
- η γέφυρα προς την απομακρυσμένη εκτέλεση σε Kubernetes από WSL

## Χρήσιμες παρατηρήσεις

- Αν το `java -version` δεν δουλεύει, κλείστε και ανοίξτε ξανά το VS Code και δημιουργήστε νέο terminal. Αν συνεχίσει να μην δουλεύει, επιστρέψτε στον οδηγό `01_workstation-setup`.
- Αν το VS Code δεν «βλέπει» σωστά το `.venv`, ξανακάντε `Python: Select Interpreter`.
- Αν δείτε warnings για `winutils.exe` ή `NativeCodeLoader`, μπορείτε να τα αγνοήσετε σε αυτό το απλό τοπικό παράδειγμα σε Windows.
- Αν το αρχείο `text.txt` δεν βρίσκεται στον σωστό κατάλογο, το πρόγραμμα θα αποτύχει επειδή δεν θα το βρει.
- Αν η πόρτα `4040` χρησιμοποιείται ήδη, το Spark μπορεί να ξεκινήσει το UI σε άλλη θύρα όπως `4041`.
- Αν αργότερα περάσετε στον οδηγό `04`, η απομακρυσμένη εκτέλεση δεν γίνεται από PowerShell αλλά μόνο από WSL.
