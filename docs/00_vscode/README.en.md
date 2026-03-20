# Apache Spark Development with VS Code

## Installing `pyspark` in VS Code with a `venv` environment

You can find the official Apache Spark programming guide here:

https://spark.apache.org/docs/latest/rdd-programming-guide.html

This guide assumes that you already have a recent version of **Visual Studio Code** installed on your computer. Instead of VS Code, you may also use any Python IDE/editor of your choice.

https://code.visualstudio.com/

It is recommended to install **Python 3.11** on your computer. In this course we use a simple local environment with `venv`, so Python 3.11 is a safe and practical choice.

https://www.python.org/downloads/

For Python development in VS Code, you should install at least the following extensions:

- `Python`
- `Pylance`
- optionally `Jupyter`

![Figure 1](images/01_vscodeextensions.png)

## Creating a new working folder

Create a new directory for your project, for example `Spark_example` under a path such as `C:\repositories`. It is important that **file names and directory names do not contain spaces**.

Open the folder in VS Code with `File -> Open Folder`.

When VS Code runs for the first time, if it asks whether you trust the folder, choose `Yes, I trust the authors`.

![Figure 2](images/02_trustauthors.png)

## Creating a virtual environment in VS Code

For this course it is recommended to use a **local virtual environment with `venv`** inside each project. This is the cleanest and most practical approach because:

- each assignment has its own packages
- conflicts between different projects are avoided
- VS Code usually detects the project's `.venv` automatically

Open your project folder in VS Code.

Open a terminal inside VS Code (`Terminal -> New Terminal`) and create the virtual environment:

```powershell
python -m venv .venv
```

The command above creates a `.venv` directory inside your project.

## Activating the virtual environment

After creating `.venv`, you have two simple options:

### Option 1: Close and reopen the terminal

In many cases it is enough to close the terminal and open a new terminal inside VS Code.  
VS Code will usually detect `.venv` automatically and activate it by itself.

### Option 2: Manual activation

If you want, you can also activate it manually from the terminal.

In Windows `cmd.exe`:

```bat
.venv\Scripts\activate.bat
```

In Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If everything worked correctly, you will usually see `(.venv)` at the beginning of the terminal prompt.

![Figure 3](images/03_autovenvactivation.png)

## Installing packages

After the virtual environment is activated, install the required packages with:

```powershell
python -m pip install pyspark psutil
```

You can view the installed packages with:

```powershell
python -m pip list
```

We prefer the `python -m pip` form instead of plain `pip`, because this makes it explicit that the installation targets the Python interpreter used by the project.

![Figure 4](images/04_pysparkinstalled.png)

## If PowerShell does not allow activation

On some Windows machines, PowerShell may not allow the execution of `Activate.ps1`.

In that case you can either:

- use `cmd.exe` with:
  ```bat
  .venv\Scripts\activate.bat
  ```
- or run once:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## If creating `.venv` gets stuck

On some machines, the command:

```powershell
python -m venv .venv
```

may be slow or appear to hang at the step where `pip` is installed inside the virtual environment.

In that case, try the following alternative:

```powershell
python -m venv --without-pip .venv
.\.venv\Scripts\python.exe -m ensurepip --upgrade
```

This way, the virtual environment is created first and `pip` is installed in a second step.

## What to remember

For this course, the recommended workflow is the following:

1. create `.venv`
2. choose `Python: Select Interpreter`
3. install packages with `python -m pip`
4. run or debug from VS Code

Manual activation is optional and is mainly useful when you work directly from a terminal.

## Installing Java on your computer

JDK 17 is required for local PySpark execution.
You do not need to install Apache Spark separately on your computer. For this guide, the `pyspark` package installed inside `.venv` plus Java is enough.

On Windows, the simplest approach is to open a PowerShell terminal and run:

```powershell
winget install --id Microsoft.OpenJDK.17 --accept-source-agreements --accept-package-agreements
```

This command installs Java and configures the required system environment variables.

During installation, Windows may show a prompt asking to run the installer with administrator privileges. In that case, choose `Yes` to continue.

If `winget` is not available on your machine, install any JDK 17 manually and make sure that:

- `JAVA_HOME` points to the Java installation directory
- the `java` command is available in `PATH`

If Java was installed while VS Code was already open, close and reopen all VS Code windows and create a new terminal, so that the new environment variables are loaded. Normally, a full computer restart is not required. Then verify that everything works correctly:

```powershell
java -version
```

## Creating example files

Create two files in your project directory: `main.py` and `text.txt`.

Put the following code into `main.py`:

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

The two lines using `sys.executable` explicitly tell Spark to use the same Python interpreter that the project has selected in VS Code. Because of that, this first example does not require a separate `launch.json`.

Put the following sample content into `text.txt`:

```text
spark spark data
big data spark
python spark
```

## Running and debugging in VS Code

After you have already selected the interpreter from `.venv`, open `main.py` and run the program in one of the following ways:

- from the `Run Python File` button
- from the integrated terminal, with `.venv` active, by using `python main.py`

For debugging:

- open `Run and Debug`
- if VS Code asks you for a debug configuration type, choose `Python Debugger: Current File`
- then press `F5`

For this simple example, that is enough. You do not need to write `launch.json` manually. If VS Code automatically creates a simple `launch.json` during the first debug run, you can keep the default configuration.

The first time you run the program, Windows Firewall / Windows Defender may show a prompt for `OpenJDK Platform binary`. If it appears, choose `Allow`, so that Spark can open the local port it needs.

![Figure 5](images/05_java_firewall.png)

If everything is configured correctly, you should see output such as:

```text
[('spark', 4), ('data', 2), ('big', 1), ('python', 1)]
```

## Experimenting with `pyspark`

If you want to experiment interactively with Spark, you have two practical options:

- `pyspark`, which opens a ready-to-use shell with `sc` and `spark` already available, but on Windows it often does not provide convenient command history with the `Up` / `Down` keys
- the regular Python console that you open with `python`, which usually has more convenient history and editing, but requires you to create the `SparkSession` manually

Note: `pyspark` is for Python, while `spark-shell` is the Scala shell. The command `sparkshell` without a dash is not valid.

### Option 1: `pyspark`

`pyspark` is the quickest option if you want to start immediately with `sc` and `spark` ready to use.

After activating `.venv` and confirming that `java -version` works, run the following in the terminal:

```powershell
$env:PYSPARK_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
$env:PYSPARK_DRIVER_PYTHON = $env:PYSPARK_PYTHON
pyspark
```

Once the shell opens, you can try commands such as:

```python
sc.parallelize([1, 2, 3]).count()
spark.range(5).show()
```

To exit the shell:

```python
exit()
```

### Option 2: open the regular Python console from the terminal

If you prefer better command history and a more predictable terminal experience, you can first open the regular Python console:

```powershell
python
```

and then create the Spark session manually:

```python
import os
import sys
from pyspark.sql import SparkSession

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

spark = SparkSession.builder.appName("playground").getOrCreate()
sc = spark.sparkContext
```

After that, you can experiment with commands such as:

```python
sc.parallelize([1, 2, 3]).count()
spark.range(5).show()
```

When you are done:

```python
spark.stop()
exit()
```

## Checking the Spark UI

Another useful way to monitor what is happening is through the URL where the Spark UI runs. During local execution, it usually appears at:

[http://localhost:4040](http://localhost:4040)

Once you stop the program, the corresponding Spark UI web server also stops.

The exact appearance of the Spark UI may differ slightly depending on the Spark version, but the general idea remains the same.

![Figure 6](images/06_spark_ui.png)

## Useful notes

- If `java -version` does not work immediately after installation, close and reopen VS Code and create a new terminal.
- If VS Code does not detect `.venv` correctly, run `Python: Select Interpreter` again.
- If you see warnings about `winutils.exe` or `NativeCodeLoader`, you can ignore them for this simple local Windows example.
- If `text.txt` is not located in the correct directory, the program will fail because it cannot find it.
- If port `4040` is already in use, Spark may start the UI on another port such as `4041`.