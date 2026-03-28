# Workstation setup (WSL + Docker Desktop)

The course includes a laboratory component in which we will use Docker containers. This guide describes the preparatory steps that should be completed before the first lab. In particular, it covers the setup of the Windows Subsystem for Linux (WSL), Ubuntu, and Docker Desktop on a personal computer.

## Enabling WSL and Virtual Machine Platform

First, you need to enable WSL and the Virtual Machine Platform feature in Windows.

**Open PowerShell as administrator:** Right-click the **Start** menu and select **Windows Terminal (Administrator)** or **PowerShell (Administrator)**.

![Figure 1](images/img1.png)

Run the following commands to enable WSL and Virtual Machine Platform. After running them, restart your computer.

```bash
wsl --install --no-distribution
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```
![Figure 2](images/img23.png)

![Figure 3](images/img20.png)

After the restart, install Ubuntu:

```bash
wsl --install -d Ubuntu
```

### Optional note for anyone testing the guide inside a Hyper-V VM

The main course path assumes that students run this guide on a personal computer, not inside a Windows virtual machine.

If, however, you are testing the guide inside a Windows virtual machine that runs on `Hyper-V`, it is not enough to enable `WSL2` only inside the guest operating system. The Hyper-V host must also expose **nested virtualization** to that VM.

If you see a message such as:

- `WSL2 is not supported with your current machine configuration`
- `HCS_E_HYPERV_NOT_INSTALLED`

then the usual cause is not the guest OS itself, but that the host has not exposed virtualization extensions to the VM.

In that case:

1. shut down the VM
2. on the **host** PowerShell as administrator run:

```powershell
Stop-VM "<Your-VM-Name>"
Set-VMProcessor -VMName "<Your-VM-Name>" -ExposeVirtualizationExtensions $true
Start-VM "<Your-VM-Name>"
```

3. inside the guest Windows, run again:

```powershell
wsl --install --no-distribution
wsl --install -d Ubuntu
```

If the problem persists, also check:

- that virtualization is enabled in the BIOS/UEFI of the physical host
- that the VM has been fully restarted after the change
- that `VirtualMachinePlatform` appears as `Enabled`

For my own test VM, the corresponding name was `Windows 11 Bigdata uth 2026`, but that is not part of the general student workflow.

### Ubuntu configuration

**Open Ubuntu:** After installation, click the **Start** menu and search for **Ubuntu**. Click it to open it.

![Figure 4](images/img4.png)

**Set up a user account and password:** The first time Ubuntu starts, you will be asked to create a user and set a password. This user will be the main user for your Ubuntu installation.

![Figure 7](images/img7.png)

### Upgrades and updates

Once Ubuntu is ready, it is a good idea to run a few commands to make sure your system is up to date.

**Upgrade system packages:** Run the following command to upgrade the system packages:

```bash
sudo apt update && sudo apt upgrade -y
```

**Check the WSL status**

Open PowerShell (as administrator) and run the following command:

```bash
wsl --list --verbose
```
![Figure 5](images/img2.png)

This command shows the installed Linux distributions and indicates which one is the default. If WSL has been installed correctly, you should see the Ubuntu distribution (or another distribution that you installed).

**Check whether Virtual Machine Platform is enabled**

To verify that Virtual Machine Platform is enabled, run the following command:

```bash
Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
```

If Virtual Machine Platform is enabled, the feature status should be **Enabled**.

**Check the current WSL version**

To check which WSL version (1 or 2) you are using, run the following command:

```bash
wsl --list --verbose
```

You will see the WSL version for each Linux distribution (for example, 2 for WSL 2 or 1 for WSL 1).

If everything is configured correctly, WSL and Virtual Machine Platform should appear as enabled, and Ubuntu or another Linux distribution should be available for use on your system.

## Installing Docker Desktop

Go to the official Docker page and download the latest version of Docker Desktop for Windows x86_64:

https://docs.docker.com/desktop/setup/install/windows-install/

**Run the installer:** Double-click the installation file you downloaded and follow the installation wizard.

![Figure 18](images/img18.png)

**Installation options:**

During installation, make sure that the **Use the WSL 2 based engine** option is selected.

![Figure 11](images/img11.png)

Docker Desktop will also install the **Docker Desktop WSL 2 Backend**, which is required in order to run Docker with WSL 2.

**Complete the installation:** When the installation finishes, click **Finish** and Docker Desktop will start automatically. The installation may take a little while. You will need to restart your computer.

![Figure 8](images/img8.png)

After the restart, you may be asked to create an account for the service. This is not mandatory, and you may choose **Skip**.

![Figure 9](images/img3.png)

**Configure Docker to use WSL 2:** After installation, you can open **Docker Desktop** from the **Start Menu**.

If this is the first time you open Docker Desktop, it may guide you through enabling WSL 2.

Make sure that **WSL 2** is selected as the backend in Docker Desktop. To check this, go to **Settings** in Docker, then to the **General** tab, and verify that **Use the WSL 2 based engine** is enabled.

![Figure 21](images/img21.png)

**Select the WSL distribution for Docker:** In the **Resources** tab of Docker Desktop, you can see which WSL Linux distributions are available for use with Docker. Make sure that the Ubuntu distribution (or another one you installed) is enabled for Docker.

![Figure 12](images/img12.png)

**Restart Docker:** If you make changes to the settings, restart Docker Desktop so that the changes take effect.

**Confirm the installation**

Open the **Ubuntu terminal** and run the following command to verify that Docker is working correctly:

```bash
docker --version
```
![Figure 10](images/img5.png)

This should display the version of Docker that you installed.

Then try running the command:

```bash
docker run hello-world
```

This command downloads and runs a simple Docker image that prints a success message if Docker is installed and working correctly.
![Figure 25](images/img25.png)

**Updates and settings**

**Update Docker:** Docker Desktop updates automatically. You can check for new versions under **Settings** > **Updates**.

**Resource settings:** In the **Resources** tab of Docker Desktop, you can configure how much CPU, memory (RAM), and disk space are available to the WSL backend.

## Tools needed by the next guides

After `01`, the course splits into two kinds of paths:

- `02` and `03`: can be completed either from `Windows / PowerShell` or from `WSL / Ubuntu`
- `04` and `05`: run only from `WSL / Ubuntu`
- `06`: is also documented with `WSL / Ubuntu` so that the shell workflow stays consistent

### For the Windows / PowerShell path

Before moving to the local guides `02` and `03`, make sure Windows already has:

- `Python 3.11`
- `Git for Windows`
- `OpenJDK 17`

The most practical and tested route in the course is to use `winget`.

From PowerShell:

```powershell
winget install --id Python.Python.3.11 -e --source winget --accept-source-agreements --accept-package-agreements
winget install --id Git.Git -e --source winget --accept-source-agreements --accept-package-agreements
winget install --id Microsoft.OpenJDK.17 -e --source winget --accept-source-agreements --accept-package-agreements
```

After the installation, close the terminal, open a new PowerShell window, and verify:

```powershell
python --version
git --version
java -version
```

The above `winget` identifiers were verified on my own machine:

- `Python.Python.3.11`
- `Git.Git`
- `Microsoft.OpenJDK.17`

An alternative also available is:

- `Microsoft.OpenJDK.11`
- `EclipseAdoptium.Temurin.11.JDK`

### OpenVPN client on Windows and lab access files

After you submit the lab form, you will receive an email with two main attachments:

- `vdcloud-k8s.ovpn`
- `config`

In the course provisioning tool, these are generated and sent with exactly these names for `vdcloud`.

If you do not already have an OpenVPN client on Windows, install the client used by the lab. In the workflow described by the email, the client usually expects `.ovpn` files under:

```text
C:\Users\<windows-username>\OpenVPN\config
```

In practice:

1. save both attachments first under your Windows `Downloads` folder
2. copy `vdcloud-k8s.ovpn` into `C:\Users\<windows-username>\OpenVPN\config`
3. open the OpenVPN client and connect with the `vdcloud-k8s.ovpn` profile

Whenever the lab sends you a new `vdcloud-k8s.ovpn`, replace the old file and reconnect.

### For the WSL / Ubuntu path

Before moving to the guides that use WSL, make sure Ubuntu already has the baseline tools:

```bash
sudo apt update
sudo apt install -y git curl tar openjdk-11-jdk
git --version
java -version
```

`kubectl`, `Spark`, and the `Hadoop` client are used from `04` onward. If you plan to follow the full lab path, make sure they are installed and configured before you continue to the remote execution guide.

For the course baseline, the recommended versions are:

- `Spark 3.5.8`
- `Hadoop client 3.4.1`
- `Java 11`

Example installation inside WSL:

```bash
cd ~

SPARK_VERSION=3.5.8
HADOOP_VERSION=3.4.1

curl -LO "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz"
tar -xzf "spark-${SPARK_VERSION}-bin-hadoop3.tgz"

curl -LO "https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz"
tar -xzf "hadoop-${HADOOP_VERSION}.tar.gz"
```

For `kubectl`, the simplest per-user installation in WSL is the official binary path:

```bash
cd ~
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
mkdir -p ~/.local/bin
mv ./kubectl ~/.local/bin/kubectl
kubectl version --client
```

## Configure VPN and kubeconfig for `vdcloud`

From the lab email, you should already have downloaded to Windows:

- `vdcloud-k8s.ovpn`
- the attached `config`

After connecting to the VPN from Windows, switch to WSL and configure kubeconfig from the attached file:

```bash
mkdir -p ~/.kube
cp /mnt/c/Users/<windows-username>/Downloads/config ~/.kube/config
chmod 600 ~/.kube/config
```

Then verify:

```bash
kubectl config current-context
kubectl config get-contexts
kubectl config view --minify --flatten | sed -n '1,40p'
kubectl get ns
```

In the configuration generated by the course provisioning tool:

- the cluster server is `https://source-code-master.cluster.local:6443`
- the contexts `development` and `<username>-priv` are created
- the default current context is set to `<username>-priv`

If `kubectl` does not work, first check:

- that the VPN is connected on Windows
- that `config` was copied correctly to `~/.kube/config`
- that `kubectl version --client` works normally inside WSL

## Next step: get the repository

Once you finish `01`, the next practical step is to have the repository locally available. For the local guides `02` and `03`, you can choose either a Windows path or a WSL path. For the remote guides `04` and `05`, you will definitely need a WSL clone.

### Option A: clone in a Windows folder

From PowerShell:

```powershell
Set-Location $HOME
git clone https://github.com/ikons/bigdata-uth.git
Set-Location bigdata-uth
```

This option is enough for the local guides `02` and `03`.

### Option B: clone inside WSL

From the Ubuntu terminal:

```bash
cd ~
git clone https://github.com/ikons/bigdata-uth.git
cd bigdata-uth
```

This option is required for the remote guides `04` and `05`, and it is also the recommended path for `06`.

### What to keep in mind

- For `02` and `03`, you may work either from PowerShell or from WSL.
- For `04` and `05`, work only from WSL.
- If you start locally on Windows, you can later create a second clone inside WSL just for the remote path.
