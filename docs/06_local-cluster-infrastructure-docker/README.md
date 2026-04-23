# Τοπική συστοιχία Spark + HDFS με το Docker Compose

Σε αυτόν τον οδηγό θα στήσετε από την αρχή, στον προσωπικό σας υπολογιστή, μια μικρή αλλά πλήρη συστοιχία Spark + HDFS με το Docker Compose. Στόχος δεν είναι μόνο να εκτελέσετε έτοιμα παραδείγματα, αλλά και να καταλάβετε ποια μέρη χρειάζονται για να λειτουργήσει μια τέτοια υποδομή και πώς συνεργάζονται μεταξύ τους.

Μέσα από τα βήματα του οδηγού θα δείτε στην πράξη τον ρόλο του NameNode, των DataNode, του κόμβου master του Spark και των κόμβων worker του Spark. Θα αρχικοποιήσετε το HDFS, θα ανεβάσετε κώδικα και δεδομένα και θα εκτελέσετε εργασίες πάνω στη συστοιχία. Οι εντολές γράφονται για WSL, ώστε η ροή να παραμείνει ενιαία και απλή για το εργαστήριο.

Ο οδηγός αυτός μπορεί να εκτελεστεί με δύο παραλλαγές Docker μέσα στο WSL:

- **Προτεινόμενη**: `Docker Desktop` με WSL integration
- **Προαιρετική, για πιο προχωρημένη χρήση**: αυτόνομος `Docker Engine` απευθείας μέσα στο Ubuntu

Από τη στιγμή που οι εντολές `docker version` και `docker compose version` λειτουργούν κανονικά στο τερματικό του WSL, οι βασικές εντολές του οδηγού είναι ίδιες και για τις δύο διαδρομές.

## Προέλεγχος Docker στο WSL

Πριν προχωρήσετε, βεβαιωθείτε ότι το ενεργό Docker CLI μέσα στο WSL επικοινωνεί κανονικά με την υπηρεσία Docker:

```bash
docker version
docker compose version
docker info --format '{{.ServerVersion}}'
```

Αν χρησιμοποιείτε `Docker Desktop`, φροντίστε πρώτα να έχει ξεκινήσει κανονικά η εφαρμογή στα Windows.

Αν χρησιμοποιείτε αυτόνομο `Docker Engine` μέσα στο WSL, ελέγξτε και:

```bash
systemctl is-active docker
```

που πρέπει να επιστρέφει `active`.



## Αρχιτεκτονική HDFS και Spark

**HDFS**: Κατανεμημένο σύστημα αρχείων, από το οποίο οι εργασίες Spark μπορούν να διαβάσουν και να γράψουν.



Ρόλοι κόμβων στη συστοιχία:
![Εικόνα 1](images/img1.png)


- **HDFS NameNode:** Ο NameNode είναι ο πιο σημαντικός κόμβος του HDFS. Γνωρίζει ποιος DataNode αποθηκεύει ποιο μπλοκ ενός αρχείου.
- **HDFS DataNode:** Οι DataNode αποθηκεύουν μπλοκ από τα αρχεία του HDFS στο τοπικό τους σύστημα αρχείων. Η δουλειά τους είναι να εξυπηρετούν τα μπλοκ που ζητούν οι πελάτες.

**Spark:** Ένα ενιαίο σύστημα κατανεμημένης επεξεργασίας δεδομένων, που περιλαμβάνει την υλοποίηση του προγραμματιστικού μοντέλου MapReduce και βιβλιοθήκες για μηχανική μάθηση, εκτέλεση SQL κ.λπ.

![Εικόνα 2](images/img2.png)

![Εικόνα 3](images/img3.png)


- **Spark Master:** Ο κόμβος master του Spark ελέγχει τους διαθέσιμους πόρους και, με βάση αυτούς, εκκινεί και διαχειρίζεται τις κατανεμημένες εφαρμογές που εκτελούνται στη συστοιχία.
- **Spark Worker:** Ο worker είναι μια διεργασία του Spark, η οποία εκτελείται σε κάθε κόμβο της συστοιχίας και διαχειρίζεται τις διεργασίες των κατανεμημένων εφαρμογών που εκτελούνται σε αυτόν τον κόμβο.
- **Spark Driver:** Ο driver του Spark λειτουργεί ως ελεγκτής της εκτέλεσης μιας εφαρμογής Spark. Διατηρεί ολόκληρη την κατάσταση της εφαρμογής που εκτελείται στη συστοιχία.




## Βασικές έννοιες Docker

**Βασικές έννοιες:** Για τη δημιουργία της παραπάνω υποδομής θα χρησιμοποιήσουμε περιέκτες Docker στον προσωπικό μας υπολογιστή. Οι βασικές έννοιες που χρειάζεται να γνωρίζουμε είναι οι εξής:

- **Εικόνα Docker**: Είναι ένα στατικό αρχείο που περιέχει όλα τα απαραίτητα για την εκτέλεση μιας εφαρμογής, συμπεριλαμβανομένου του κώδικα, των εξαρτήσεων και του λειτουργικού περιβάλλοντος. Για να εκτελεστεί ένας περιέκτης, πρέπει πρώτα να υπάρχει η αντίστοιχη εικόνα, συνήθως από κάποιο αποθετήριο εικόνων. Για παράδειγμα, με την παρακάτω εντολή κατεβάζουμε την επίσημη εικόνα `hello-world` και εκτελούμε έναν περιέκτη που βασίζεται σε αυτήν:

```bash
docker run hello-world
```

- **Dockerfile:** Είναι ένα αρχείο κειμένου που περιέχει οδηγίες για τη δημιουργία μιας εικόνας Docker. Μέσω αυτού καθορίζουμε τη βάση της εικόνας, τις εξαρτήσεις και τις ρυθμίσεις εκτέλεσης. Παράδειγμα δημιουργίας ενός `Dockerfile` που χρησιμοποιεί την εικόνα Python και εκτελεί ένα τοπικό αρχείο `app.py`.

Ανοίγουμε το τερματικό Ubuntu και τρέχουμε

```bash
mkdir compose-example
cd compose-example
```

Δημιουργώ το τοπικό αρχείο app.py

```bash
nano app.py
```

Γράφω στον editor

```python
print("Hello from Docker!")
```

Αποθηκεύστε το (`CTRL` + `X`, μετά `Y` και `Enter`).

Τώρα δημιουργώ το τοπικό αρχείο Dockerfile
```bash
nano Dockerfile
```

Γράφω στον editor

```dockerfile
FROM python:3.9
COPY app.py /app.py
CMD ["python", "/app.py"]
```

Αποθηκεύστε το (`CTRL` + `X`, μετά `Y` και `Enter`).

Το χτίζουμε και το τρέχουμε με τις παρακάτω εντολές

```bash
docker build -t my-python-app .
```


![Εικόνα 4](images/img4.png)


```bash
docker run my-python-app
```


Η παρακάτω εντολή εκτελεί την εικόνα που μόλις χτίσαμε ως περιέκτη:

![Εικόνα 5](images/img5.png)



Την πρώτη φορά που το τρέχουμε «κατεβάζει» τις απαραίτητες εξαρτήσεις. Τις επόμενες φορές δεν χρειάζεται



- **Docker Compose:** Είναι ένα εργαλείο που επιτρέπει τη διαχείριση πολλών περιεκτών μέσω ενός αρχείου σύνθεσης, ορίζοντας υπηρεσίες, δίκτυα και αποθηκευτικούς χώρους.
- Οι περιέκτες Docker έχουν **εφήμερο** σύστημα αρχείων, το οποίο χάνεται όταν τερματιστούν.
- **Τόμος (`Volume`)**: Είναι ένας μηχανισμός αποθήκευσης δεδομένων που επιτρέπει στους περιέκτες να διατηρούν δεδομένα ακόμη και μετά την επανεκκίνηση ή διαγραφή τους. Για τη μόνιμη αποθήκευση αρχείων, το Docker χρησιμοποιεί μόνιμους τόμους. Οι τόμοι μπορούν να δημιουργηθούν, να αποκτήσουν δικό τους όνομα και να προσαρτηθούν στους περιέκτες που δημιουργούνται.



## Δημιουργία τοπικής συστοιχίας Apache Spark και HDFS με περιέκτες Docker




Περιηγηθείτε στον κατάλογο του παραδείγματος

```bash
cd ~/bigdata-uth/docker/stacks/local-spark-hdfs/
```



Στον κατάλογο θα δείτε τα παρακάτω αρχεία:

- **compose.yml**: αρχείο που δημιουργεί τοπικά στον υπολογιστή σας μια υποδομή που αποτελείται από:
   - 1 συστοιχία HDFS με έναν `namenode` και 3 `datanode` (`datanode1`, `datanode2`, `datanode3`).
   - 1 συστοιχία Spark με έναν `spark-master` και 4 `spark-worker` (`spark-worker1`, `spark-worker2`, `spark-worker3`, `spark-worker4`).
   - 1 υπηρεσία μίας εκτέλεσης για την αρχικοποίηση του HDFS (όνομα: `hdfs-init`).
   - 1 ξεχωριστός διακομιστής ιστορικού εκτελέσεων Spark (όνομα: `spark-history`).

Η στοίβα αυτή χτίζεται από κοινά αρχεία και καταλόγους του `docker/`:

- `docker/images/spark-master/`: επαναχρησιμοποιήσιμη εικόνα για τον `spark-master`
- `docker/images/spark-worker/`: επαναχρησιμοποιήσιμη εικόνα για τους `spark-worker`
- `docker/images/spark-history/`: επαναχρησιμοποιήσιμη εικόνα για τον ξεχωριστό διακομιστή ιστορικού
- `docker/shared/spark/spark-defaults.conf`: κοινές ρυθμίσεις Spark για την τοπική στοίβα
- `docker/shared/scripts/hdfs-init.sh`: βοηθητικό πρόγραμμα μίας εκτέλεσης για την αρχικοποίηση του HDFS
- `docker/shared/hadoop-conf/local-hdfs/`: ρυθμίσεις του πελάτη Hadoop για το τοπικό HDFS
- `init-hdfs.sh`: προαιρετικό βοηθητικό πρόγραμμα στον υπολογιστή σας για χειροκίνητη επανεκτέλεση του `hdfs-init`

## Πώς συνδέονται οι υπηρεσίες μεταξύ τους

Πριν ξεκινήσετε τις εντολές, αξίζει να δείτε καθαρά το μοντέλο επικοινωνίας της τοπικής συστοιχίας:

- Όλοι οι περιέκτες μπαίνουν στο ίδιο δίκτυο Docker `hadoop-net`.
- Μέσα σε αυτό το δίκτυο, τα ονόματα υπηρεσιών του `compose.yml` λειτουργούν και ως ονόματα υπολογιστών.
- Άρα ο κόμβος `spark-master` βρίσκει το HDFS ως `hdfs://namenode:9000` και οι `spark-worker` βρίσκουν τον κόμβο master ως `spark://spark-master:7077`.
- Οι εργασίες Spark υποβάλλονται από τον περιέκτη `spark-master`, αλλά τα δεδομένα τους βρίσκονται στο HDFS της ίδιας συστοιχίας.
- Η υπηρεσία μίας εκτέλεσης `hdfs-init` περιμένει να γίνει διαθέσιμο το HDFS και δημιουργεί αυτόματα τους καταλόγους `/user/root`, `/user/root/examples` και `/logs`.
- Ο ξεχωριστός περιέκτης `spark-history` διαβάζει τα αρχεία καταγραφής συμβάντων του Spark από το HDFS, ώστε να μπορεί να εμφανίζει ολοκληρωμένες εργασίες ακόμη και αφού έχουν τερματιστεί οι εκτελεστές.
- Οι ονομασμένοι τόμοι διατηρούν μόνιμα τα μεταδεδομένα του HDFS, τα μπλοκ του HDFS και τους φακέλους προσωρινής μεταφόρτωσης αρχείων, ώστε να μη χάνονται με κάθε επανεκκίνηση των περιεκτών.

Με άλλα λόγια:

- ο `namenode` και οι `datanodes` συγκροτούν το HDFS
- ο `spark-master` και οι `spark-worker1-4` συγκροτούν τη συστοιχία Spark
- ο `spark-history` είναι ξεχωριστή υπηρεσία παρακολούθησης και δεν τρέχει μέσα στον `spark-master`
- το κοινό δίκτυο Docker επιτρέπει στα δύο υποσυστήματα να επικοινωνούν με ονόματα όπως `namenode` και `spark-master`
- το `hdfs-init` φροντίζει αυτόματα την αρχική δομή καταλόγων του HDFS
- το HDFS είναι το κοινό στρώμα αποθήκευσης που χρησιμοποιούν τόσο οι εργασίες Spark όσο και ο διακομιστής ιστορικού

**Εκκίνηση υποδομής:** Εκτελέστε την παρακάτω εντολή για να σηκώσετε την υποδομή. **Προσοχή**: πρέπει να βρίσκεστε μέσα στον κατάλογο `docker/stacks/local-spark-hdfs` για να λειτουργήσει σωστά:

```bash
docker compose up --build -d
```

Σε αυτή την εκδοχή της στοίβας, η αρχικοποίηση του HDFS γίνεται αυτόματα από την υπηρεσία `hdfs-init`. Δεν χρειάζεται πλέον να εκτελέσετε χειροκίνητα το `init-hdfs.sh` στη βασική διαδρομή του οδηγού.

Την πρώτη φορά που θα εκτελέσετε την εντολή μπορεί να χρειαστούν αρκετά λεπτά, ειδικά αν η υπηρεσία Docker μόλις ξεκίνησε ή αν πρέπει να κατεβούν μεγάλες εικόνες. Αν δείτε καθυστέρηση, πρώτα επιβεβαιώστε ότι το `docker version` λειτουργεί κανονικά μέσα από το τερματικό του WSL και αφήστε λίγο χρόνο στην υπηρεσία Docker να ολοκληρώσει την εκκίνησή της.

Εάν όλα πάνε καλά, θα δείτε τους περιέκτες να ξεκινούν κανονικά. Αν χρησιμοποιείτε Docker Desktop, θα τους δείτε και στο γραφικό περιβάλλον της εφαρμογής (πράσινη κουκκίδα).

![Εικόνα 6](images/img6.png)

Αντίστοιχα, μπορείτε να εκτελέσετε από το τερματικό την παρακάτω εντολή για να δείτε τους περιέκτες:

```bash
docker ps
```
![Εικόνα 7](images/img7.png)

Αν χρησιμοποιείτε Docker Desktop, μπορείτε να κάνετε κλικ στο `local-spark-hdfs` και να δείτε τους επιμέρους περιέκτες που εκτελούνται:

![Εικόνα 8](images/img8.png)

Για κάθε περιέκτη όπου βλέπετε ζεύγη αριθμών, για παράδειγμα `9870:9870` για τον `namenode`, σημαίνει ότι εκθέτει μία **υπηρεσία**. Συνήθως πρόκειται για μια ιστοσελίδα διαχείρισης, αλλά όχι απαραίτητα. Η υπηρεσία αυτή είναι **προσβάσιμη από το λειτουργικό σύστημα του υπολογιστή σας**, είτε ανοίγοντας απευθείας το αντίστοιχο URL είτε επικολλώντας το στον φυλλομετρητή.

Για παράδειγμα, ο περιέκτης `namenode` εξυπηρετεί τη σελίδα:

http://localhost:9870

![Εικόνα 9](images/img9.png)

Αντίστοιχα, ο `spark-master` προσφέρει τη διεπαφή που δείχνει τους κόμβους worker και τις εργασίες του στη διεύθυνση http://localhost:18080, ενώ ο ξεχωριστός `spark-history` προσφέρει τον διακομιστή ιστορικού στη διεύθυνση http://localhost:18081, όπου εμφανίζονται οι εργασίες που έχουν ήδη εκτελεστεί.

Χρησιμοποιούμε τις θύρες `18080` και `18081` αντί για `8080` και `8081`, γιατί σε αρκετά συστήματα Windows + WSL οι χαμηλότερες θύρες δεσμεύονται από τη στοίβα εικονικοποίησης και δικτύωσης και δεν προωθούνται αξιόπιστα στο `localhost`.

![Εικόνα 10](images/img10.png)

Στην ενότητα **Volumes** βλέπετε όλους τους μόνιμους τόμους που χρησιμοποιεί η υποδομή σας. Οι μόνιμοι τόμοι έχουν δηλωθεί στο `compose.yml` και δημιουργήθηκαν με την εντολή `docker compose up`.

![Εικόνα 11](images/img11.png)


Αντίστοιχα, μπορείτε να εκτελέσετε από το τερματικό την παρακάτω εντολή για να δείτε τους τόμους:

```bash
docker volume ls
```

![Εικόνα 12](images/img12.png)

Το πού ακριβώς βρίσκονται οι τόμοι Docker εξαρτάται από τη διαδρομή εγκατάστασης του Docker που χρησιμοποιείτε.

### Αν χρησιμοποιείτε Docker Desktop

Στην περίπτωση αυτή, η υπηρεσία Docker δεν τρέχει μέσα στο Ubuntu του WSL αλλά μέσα στην υποδομή `docker-desktop`.

Για να καταλάβετε τι εννοώ, ανοίξτε ένα κέλυφος των Windows (δεξί κλικ στο σύμβολο των Windows) και επιλέξτε Terminal.

![Εικόνα 13](images/img13.png)


Εκτελέστε την παρακάτω εντολή

```bash
wsl -l -v
```

![Εικόνα 14](images/img14.png)

Αυτό που βλέπουμε είναι ότι ο υπολογιστής μας εκτελεί 2 εικονικές μηχανές: η μία είναι η Ubuntu, από την οποία εκτελούμε τις εντολές Docker, και η άλλη είναι η `docker-desktop`. Η `docker-desktop` είναι αυτή που εκτελεί την υπηρεσία Docker που σηκώνει τους περιέκτες.

Οι μόνιμοι τόμοι είναι κατάλογοι στο σύστημα αρχείων της εικονικής μηχανής `docker-desktop`.

Οι μόνιμοι τόμοι της εικονικής μηχανής `docker-desktop` μπορούν να γίνουν προσβάσιμοι μέσω του συστήματος αρχείων του υπολογιστή Windows μέσω ενός συγκεκριμένου φακέλου με την ονομασία

```
\\wsl.localhost\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes
```

Ανοίγουμε έναν εξερευνητή αρχείων των Windows και επικολλούμε την παραπάνω διαδρομή στη γραμμή διεύθυνσης. Εκεί βλέπουμε όλους τους φακέλους που χρησιμοποιούνται ως μόνιμοι τόμοι από τους περιέκτες Docker και μπορούμε να τους διαχειριστούμε μέσω του συστήματος αρχείων των Windows. Κάθε κατάλογος έχει έναν υποκατάλογο `_data`, στον οποίο ό,τι τοποθετούμε είναι ορατό στους περιέκτες που έχουν προσαρτήσει τον συγκεκριμένο τόμο.

![Εικόνα 15](images/img15.png)

### Αν χρησιμοποιείτε αυτόνομο Docker Engine μέσα στο WSL

Στην περίπτωση αυτή, δεν υπάρχει ξεχωριστή εικονική μηχανή `docker-desktop`. Η υπηρεσία Docker τρέχει μέσα στο ίδιο το Ubuntu του WSL και οι τόμοι βρίσκονται στο σύστημα αρχείων του, συνήθως κάτω από:

```bash
/var/lib/docker/volumes
```

Μπορείτε να δείτε τους φακέλους τους με:

```bash
sudo ls /var/lib/docker/volumes
```

ή να εξετάσετε έναν συγκεκριμένο τόμο με:

```bash
sudo ls /var/lib/docker/volumes/<volume-name>/_data
```

Στο εργαστήριο όμως προτιμούμε να δουλεύουμε με `docker cp` και `docker exec`, ώστε τα βήματα να είναι ίδια και στις δύο διαδρομές.


**Αρχικοποίηση του συστήματος αρχείων HDFS:** Την πρώτη φορά που θα δημιουργήσετε την υποδομή, η υπηρεσία μίας εκτέλεσης `hdfs-init` θα δημιουργήσει αυτόματα τους απαραίτητους καταλόγους στο HDFS για μεταφόρτωση αρχείων και για αποθήκευση των αρχείων καταγραφής συμβάντων του Spark.

Η λογική αυτή έχει ενσωματωθεί στην ίδια τη διάταξη του Docker Compose, ώστε:

- να μη χρειάζεται χειροκίνητο βήμα μετά το `docker compose up --build -d`
- να μπορεί να επανεκτελείται με ασφάλεια χωρίς να χαλάει την ήδη υπάρχουσα δομή
- να ξεκινά ο `spark-history` ως ξεχωριστός περιέκτης αφού έχει ήδη προετοιμαστεί το HDFS

Το βοηθητικό πρόγραμμα μίας εκτέλεσης που το κάνει αυτό είναι το εξής:

<!-- AUTO-CODE: docker/shared/scripts/hdfs-init.sh -->
``` bash
#!/usr/bin/env bash

set -euo pipefail

MAX_ATTEMPTS="${MAX_ATTEMPTS:-60}"
SLEEP_SECONDS="${SLEEP_SECONDS:-2}"
HDFS_URI="${HDFS_URI:-hdfs://namenode:9000}"
HDFS_BIN="${HDFS_BIN:-/opt/hadoop-3.2.1/bin/hdfs}"

hdfs_cmd() {
  "${HDFS_BIN}" "$@"
}

wait_for_hdfs_rpc() {
  local attempt
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    if hdfs_cmd dfsadmin -fs "${HDFS_URI}" -report >/dev/null 2>&1; then
      echo "HDFS RPC endpoint is responding."
      return 0
    fi
    echo "HDFS RPC attempt ${attempt}/${MAX_ATTEMPTS}: not ready yet"
    sleep "$SLEEP_SECONDS"
  done

  echo "HDFS RPC endpoint did not become ready in time." >&2
  return 1
}

wait_for_safe_mode_to_end() {
  local attempt safe_mode_output
  for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
    safe_mode_output="$(hdfs_cmd dfsadmin -fs "${HDFS_URI}" -safemode get 2>/dev/null || true)"
    echo "safe mode attempt ${attempt}/${MAX_ATTEMPTS}: ${safe_mode_output:-unknown}"
    if ! printf '%s' "$safe_mode_output" | grep -q 'Safe mode is ON'; then
      return 0
    fi
    sleep "$SLEEP_SECONDS"
  done

  echo "HDFS stayed in safe mode for too long." >&2
  return 1
}

echo "Waiting for the HDFS RPC endpoint to respond..."
wait_for_hdfs_rpc

# Ask HDFS to leave safe mode when it is already ready enough to accept admin commands.
# If it has already left safe mode, this is a harmless no-op.
hdfs_cmd dfsadmin -fs "${HDFS_URI}" -safemode leave >/dev/null 2>&1 || true

echo "Waiting for HDFS safe mode to end..."
wait_for_safe_mode_to_end

# -mkdir -p makes the bootstrap idempotent. Re-running it repairs the expected
# lab directories without requiring manual cleanup of the whole stack.
echo "Creating the lab directories in HDFS..."
hdfs_cmd dfs -fs "${HDFS_URI}" -mkdir -p /user/root /user/root/examples /logs

echo "HDFS bootstrap completed."
```
<!-- END AUTO-CODE -->

Αν για λόγους διάγνωσης ή επαναφοράς θέλετε να ξανατρέξετε χειροκίνητα την αρχικοποίηση, μπορείτε προαιρετικά να εκτελέσετε από τον ίδιο κατάλογο:

```bash
bash ./init-hdfs.sh
```

Ο λόγος που δημιουργούμε τον `/logs` στο HDFS είναι ότι ο διακομιστής ιστορικού δεν διαβάζει αρχεία καταγραφής από το τοπικό σύστημα αρχείων του υπολογιστή. Διαβάζει τα αρχεία καταγραφής συμβάντων του Spark από το ίδιο HDFS που χρησιμοποιούν και οι εργασίες.


![Εικόνα 16](images/img16.png)

## Εκτέλεση προγραμμάτων στη συστοιχία

Εκτελέστε την παρακάτω εντολή για να υπολογίσετε το π με προσομοίωση Monte Carlo σε Java.

```bash
docker exec spark-master /opt/spark/bin/spark-submit --class org.apache.spark.examples.JavaSparkPi /opt/spark/examples/jars/spark-examples.jar
```

Όπου εάν εκτελεστεί σωστά, θα δείτε στην οθόνη να τυπώνεται (μεταξύ άλλων μηνυμάτων) το εξής:

```
Pi is roughly 3.14638
```

Εκτελέστε την παρακάτω εντολή για τον ίδιο υπολογισμό σε Python.

```bash
docker exec spark-master /opt/spark/bin/spark-submit /opt/spark/examples/src/main/python/pi.py
```

**Εκτέλεση δικού σας προγράμματος στη συστοιχία:** Τώρα που έχουμε ένα αρχικοποιημένο σύστημα αρχείων HDFS και τους περιέκτες να λειτουργούν σωστά, μπορούμε να εκτελέσουμε τα πρώτα μας προγράμματα Spark. Για τον σκοπό αυτό, πρέπει να ανεβάσουμε τα εξής στη συστοιχία:

- Αρχεία με **κώδικα** (πχ σε python).
- Αρχεία με **δεδομένα** στα οποία θα γίνει επεξεργασία (πχ τα κείμενα στα οποία θα τρέξει ένα wordcount).

**Ανέβασμα κώδικα**: Για τη ροή που βασίζεται στο αποθετήριο, ο προτεινόμενος τρόπος είναι το `docker cp` από το κλωνοποιημένο αποθετήριο και όχι η χειροκίνητη αντιγραφή μέσα σε διαδρομές τόμων. Έτσι τα βήματα παραμένουν ίδια είτε χρησιμοποιείτε Docker Desktop είτε αυτόνομο Docker Engine μέσα στο WSL.

![Εικόνα 17](images/img17.png)

Από τερματικό WSL τρέξτε:

```bash
docker cp ~/bigdata-uth/code/wordcount.py spark-master:/mnt/upload/wordcount.py
```


![Εικόνα 18](images/img18.png)

Πλέον, ο περιέκτης `spark-master` έχει στο τοπικό σύστημα αρχείων του το αρχείο `wordcount.py` στον κατάλογο `/mnt/upload`, όπως μπορείτε να δείτε εκτελώντας την παρακάτω εντολή:

```bash
docker exec spark-master ls /mnt/upload 
```

![Εικόνα 24](images/img24.png)

Η παρακάτω εντολή τυπώνει τα περιεχόμενα του απομακρυσμένου αρχείου wordcount.py (που βρίσκεται στο σύστημα αρχείων του περιέκτη spark-master):

```bash
docker exec spark-master cat /mnt/upload/wordcount.py 
```
Και θα δείτε το αρχείο `wordcount.py` να τυπώνεται. Το πρόγραμμα που χρησιμοποιούμε είναι πλέον το ίδιο κοινό πρόγραμμα του αποθετηρίου και μπορεί να τρέξει είτε τοπικά είτε σε συστοιχία, ανάλογα με το `--base-path` που θα του δώσουμε:

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

Αν αλλάξετε το `wordcount.py` στο αποθετήριο, επαναλάβετε το `docker cp` ώστε να περάσει η νεότερη έκδοση μέσα στον περιέκτη.

Ο κώδικας αντιγράφεται στον `spark-master`, γιατί από εκεί εκτελείται το `spark-submit`. Αντίθετα, τα δεδομένα δεν μένουν στο τοπικό σύστημα αρχείων του `spark-master`, αλλά ανεβαίνουν στο HDFS ώστε να είναι διαθέσιμα σε όλη τη συστοιχία.

**Ανέβασμα αρχείων δεδομένων**: Το `wordcount.py` περιμένει από το `--base-path` έναν βασικό κατάλογο που περιέχει τον υποκατάλογο `examples/` με τα αρχεία εισόδου. Αυτή τη στιγμή όμως, το σύστημα αρχείων HDFS είναι κενό, εκτός από τους δύο καταλόγους που δημιουργήσαμε σε προηγούμενο βήμα.

Θα χρειαστεί να ανεβάσουμε ένα αρχείο δεδομένων στο HDFS, ώστε να τρέξουμε το `wordcount` με είσοδο αυτό το αρχείο.

Το ανέβασμα θα γίνει σε **δύο στάδια**. Αρχικά θα τοποθετήσουμε ένα αρχείο από το τοπικό μας σύστημα αρχείων στο σύστημα αρχείων του περιέκτη `namenode`.

Κατόπιν θα εκτελέσουμε την εντολή `hdfs dfs -put` από τον περιέκτη `namenode`, με την οποία θα μεταφορτώσουμε το αρχείο από το τοπικό σύστημα αρχείων του περιέκτη, δηλαδή από τον κατάλογο `/mnt/upload`, στο σύστημα αρχείων του HDFS.

Για τον σκοπό αυτό χρησιμοποιούμε πάλι `docker cp`, αυτή τη φορά για να αντιγράψουμε το βασικό dataset στον `namenode`.

Από τερματικό WSL τρέξτε:

```bash
docker cp ~/bigdata-uth/examples/text.txt namenode:/mnt/upload/text.txt
```

![Εικόνα 19](images/img19.png)


Πλέον, ο περιέκτης `namenode` έχει στο τοπικό σύστημα αρχείων του το αρχείο `text.txt` στον κατάλογο `/mnt/upload`, όπως μπορείτε να δείτε εκτελώντας την παρακάτω εντολή:

```bash
docker exec namenode ls -lah /mnt/upload 
```

![Εικόνα 20](images/img20.png)

Πλέον, με τις παρακάτω εντολές ανεβάζουμε στο HDFS το αρχείο `text.txt` που βρίσκεται στο τοπικό σύστημα αρχείων του `namenode` στον κατάλογο `/mnt/upload`. Δημιουργούμε πρώτα τον κατάλογο `/user/root/examples`, γιατί εκεί θα ψάξει το πρόγραμμα όταν του δώσουμε `--base-path hdfs://namenode:9000/user/root`:

```bash
docker exec namenode hdfs dfs -mkdir -p /user/root/examples
docker exec namenode hdfs dfs -put -f /mnt/upload/text.txt /user/root/examples/text.txt
```

Τώρα έχουμε τοποθετήσει το αρχείο Python προς εκτέλεση στο τοπικό σύστημα αρχείων του `spark-master` και το αρχείο `text.txt` στο HDFS. Είμαστε έτοιμοι να εκτελέσουμε το Spark πρόγραμμα με την παρακάτω εντολή:

```bash
docker exec spark-master /opt/spark/bin/spark-submit /mnt/upload/wordcount.py \
  --base-path hdfs://namenode:9000/user/root
```

Σε αυτό το παράδειγμα:

- το input διαβάζεται από το `hdfs://namenode:9000/user/root/examples/text.txt`
- το output γράφεται αυτόματα σε νέο κατάλογο της μορφής `hdfs://namenode:9000/user/root/wordcount_output_<app-id>`
- έτσι μπορείτε να ξανατρέχετε το παράδειγμα χωρίς να σβήνετε κάθε φορά το προηγούμενο output

Σε αυτό το σημείο η ακολουθία είναι η εξής:

- ο οδηγός εκτέλεσης (`driver`) ξεκινά μέσα από τον `spark-master`
- ο `spark-master` αναθέτει εργασία στους διαθέσιμους κόμβους worker
- οι κόμβοι worker διαβάζουν τα δεδομένα από το `hdfs://namenode:9000`
- τα αρχεία καταγραφής συμβάντων της εκτέλεσης γράφονται επίσης στο HDFS
- ο ξεχωριστός `spark-history` τα διαβάζει αργότερα από εκεί για να εμφανίσει το ιστορικό

## Προαιρετικά: Τα ίδια βασικά αρχεία κώδικα στην τοπική συστοιχία

Αυτή η ενότητα δεν είναι μέρος του βασικού πρώτου περάσματος του μαθήματος. Η βασική μαθησιακή διαδρομή παραμένει:

- `03_local-spark-workbook`
- `04_remote-spark-kubernetes`
- `05_cluster-queries-rdd-df-sql`

Το παρακάτω το χρησιμοποιούμε ως δεύτερο πέρασμα, μόνο για να δείξουμε ότι ο ίδιος βασικός κώδικας μπορεί να τρέξει και πάνω στην τοπική συστοιχία Spark + HDFS.

Η βασική ιδέα είναι:

- ο κώδικας μένει ο ίδιος
- τα δεδομένα μένουν τα ίδια
- αλλάζει μόνο ο στόχος εκτέλεσης και η βασική διαδρομή HDFS

Από τη ρίζα του αποθετηρίου `~/bigdata-uth`, ανεβάστε ολόκληρο το βασικό `code/` στον `spark-master` και τα `examples/` στον `namenode`:

```bash
docker exec spark-master mkdir -p /mnt/upload/code
docker exec namenode mkdir -p /mnt/upload/examples
docker cp ./code/. spark-master:/mnt/upload/code/
docker cp ./examples/. namenode:/mnt/upload/examples/
docker exec namenode bash -c 'hdfs dfs -rm -r -f /user/root/examples || true; hdfs dfs -mkdir -p /user/root/examples; hdfs dfs -put -f /mnt/upload/examples/* /user/root/examples/'
```

Σε αυτή την τοπική στοίβα:

- το βασικό αρχείο κώδικα για το `spark-submit` βρίσκεται στο `/mnt/upload/code/...` του `spark-master`
- τα input datasets ζουν στο `hdfs://namenode:9000/user/root/examples/...`
- το `--base-path` είναι `hdfs://namenode:9000/user/root`
- δεν χρησιμοποιείς `/user/$VDCLOUD_USER`, όπως στην απομακρυσμένη ροή Kubernetes

Δοκίμασε πρώτα ένα μικρό σύνολο δοκιμών φορητότητας με 3 αρχεία:

```bash
docker exec spark-master /opt/spark/bin/spark-submit /mnt/upload/code/wordcount.py \
  --base-path hdfs://namenode:9000/user/root

docker exec spark-master /opt/spark/bin/spark-submit /mnt/upload/code/DFQ1.py \
  --base-path hdfs://namenode:9000/user/root

docker exec spark-master /opt/spark/bin/spark-submit /mnt/upload/code/SQLQ2.py \
  --base-path hdfs://namenode:9000/user/root
```

Μετά την εκτέλεση, ελέγξτε τα outputs στο τοπικό HDFS:

```bash
docker exec namenode hdfs dfs -ls /user/root
```

Αν όλα έχουν πάει σωστά, αυτό σημαίνει ότι το αποθετήριο πετυχαίνει τον στόχο του:

- μία κοινή βάση κώδικα
- τοπική εκτέλεση χωρίς συστοιχία
- απομακρυσμένη εκτέλεση σε έτοιμη συστοιχία Kubernetes
- και προαιρετικά εκτέλεση και σε τοπική συστοιχία Spark + HDFS

Παρακολούθηση της εκτέλεσης της τρέχουσας εργασίας: Μπορείτε να δείτε την εργασία που έχετε στείλει για εκτέλεση στην σελίδα http://localhost:18080 

![Εικόνα 21](images/img21.png)

## Διακομιστής ιστορικού

Το Apache Spark έχει μια χρήσιμη υπηρεσία που αποθηκεύει όλα τα αρχεία καταγραφής από όλους τους κόμβους, δηλαδή από τον master και τους worker, για όλες τις εργασίες που έχουν υποβληθεί. Σε αυτή την εκδοχή της στοίβας, ο διακομιστής ιστορικού τρέχει ως ξεχωριστός περιέκτης `spark-history` και είναι διαθέσιμος μέσω της σελίδας http://localhost:18081.

![Εικόνα 22](images/img22.png)

![Εικόνα 23](images/img23.png)

**Χρήσιμες εντολές Linux**

| Εντολή | Σημασία |
| --- | --- |
| `ls` | εμφάνιση περιεχομένων καταλόγου |
| `pwd` | εμφάνιση του τρέχοντος καταλόγου |
| `cd` | αλλαγή τρέχοντος καταλόγου |
| `cp` | αντιγραφή αρχείου ή καταλόγου |
| `mv` | μετακίνηση ή μετονομασία |
| `cat` | εμφάνιση περιεχομένων αρχείου |
| `echo` | εμφάνιση κειμένου στην οθόνη |
| `man <command>` | οδηγίες χρήσης για την εντολή `<command>` |

**Χρήσιμες εντολές HDFS**

Δημιουργία φακέλου στο HDFS
```bash
docker exec namenode hadoop fs -mkdir -p <path>
```

Διαγραφή φακέλου στο HDFS
```bash
docker exec namenode hdfs dfs -rm -r -f <path>			

```

Ανέβασμα αρχείου με αντικατάσταση υπάρχοντος

```bash
docker exec namenode hdfs dfs -put -f <local-path> <hdfs-path>
```

## Τερματισμός και καθαρισμός υποδομής

**Τερματισμός υποδομής**: Με την παρακάτω εντολή σταματάτε την υποδομή. Τα αρχεία που έχουν ανέβει στο HDFS ή έχουν αποθηκευτεί στους μόνιμους τόμους του `namenode` και του `spark-master` δεν διαγράφονται και παραμένουν διαθέσιμα. Όπως και για την `docker compose up`, θα χρειαστεί να βρίσκεστε στον κατάλογο που περιέχει το αρχείο `compose.yml`.

```bash
docker compose down
```

**Καθαρισμός υποδομής**: Αν θέλετε να επιστρέψετε σε καθαρή αρχική κατάσταση, εκτελέστε την παρακάτω εντολή:

```bash
docker compose down -v --remove-orphans
```

Με αυτή την εντολή:

- σταματούν και αφαιρούνται οι περιέκτες της άσκησης
- αφαιρείται το τοπικό δίκτυο της άσκησης
- διαγράφονται οι μόνιμοι τόμοι, άρα χάνονται τα δεδομένα του HDFS, τα μεταφορτωμένα αρχεία και τα αρχεία καταγραφής

Την επόμενη φορά που θα εκτελέσετε `docker compose up --build -d`, θα ξεκινήσετε από καθαρή κατάσταση και η αρχικοποίηση του HDFS θα γίνει ξανά αυτόματα.
