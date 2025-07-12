# ESMFold and GATSol Setup Guide on Google Cloud VM

This document outlines the steps taken to set up and run ESMFold and GATSol on a Google Cloud Platform (GCP) Virtual Machine (VM). It includes troubleshooting common dependency and disk space issues.

## 1. Initial VM Setup and Environment

*   **VM Configuration:** GCP VM with NVIDIA L4 GPU, running Ubuntu (Focal 20.04).
*   **CUDA Version:** 12.4 (driver version).
*   **Initial Goal:** Integrate ESMFold for protein structure prediction and ensure compatibility with existing solubility prediction pipelines (e.g., GATSol).

## 2. Challenges with Direct ESMFold Installation (Conda)

Initial attempts to install ESMFold directly into a `conda` environment (`esmfold`) faced significant dependency conflicts:

*   **Missing `openfold`:** ESMFold requires `openfold`, which was installed from its GitHub repository.
*   **`ModuleNotFoundError: No module named 'torch._six'`:** This critical error arose due to incompatibility between PyTorch 12.1 and older DeepSpeed versions used by OpenFold. Attempts to upgrade DeepSpeed led to complex build errors (Triton, CUDA incompatibilities) and circular dependency issues.

**Conclusion:** Direct `conda`/`pip` installation proved too complex and unstable due to deep-seated dependency conflicts.

## 3. Solution: Docker Containerization for ESMFold

Docker was adopted to provide a robust, isolated, and reproducible environment for ESMFold, bypassing host system dependency conflicts.

### 3.1 Docker Installation on VM

Follow the official Docker installation guide for Ubuntu. Example commands (verify latest):

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### 3.2 NVIDIA Container Toolkit Installation

Required for Docker to access the GPU:

```bash
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/ubuntu2004/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### 3.3 Cloning the ESMFold Docker Image Repository

The official `facebookresearch/esm` repository's `Dockerfile.esmfold` was missing. A community-maintained repository was used instead:

```bash
cd ~
git clone https://github.com/biochunan/esmfold-docker-image.git
cd esmfold-docker-image
```

### 3.4 Troubleshooting Docker Build Issues

*   **`ERROR: failed to read dockerfile: no such file or directory`:** Initially, `Dockerfile.esmfold` was incorrectly assumed. The correct Dockerfile was found to be `Dockerfiles/Dockerfile.root`.
*   **`GPG error: ... At least one invalid signature was encountered.`:** This indicated expired GPG keys for `apt` repositories within the Docker build environment. The `Dockerfile.root` needed modification.
*   **`No space left on device`:** The VM's disk became full (100% usage), preventing file writes and Docker builds. This was the root cause of many issues.

### 3.5 Resolving Disk Space Issues

To free up space (identified `/home/david_nunn/miniconda3` as a major consumer):

1.  **Check Disk Usage:**
    ```bash
df -h
    ```

2.  **Clean Docker System:**
    ```bash
docker system prune -a
    ```

3.  **Clean Conda Cache and Unused Packages:**
    ```bash
conda clean --all
    ```

4.  **Remove Unused Conda Environments (e.g., failed `esmfold` env):**
    ```bash
conda env remove --name esmfold
    ```

### 3.6 Modifying `Dockerfile.root` (Manual Step)

Due to persistent issues with automated file modification, this step was performed manually:

1.  **Navigate to the repository:**
    ```bash
cd ~/esmfold-docker-image
    ```

2.  **Open `Dockerfiles/Dockerfile.root` in `nano`:**
    ```bash
nano Dockerfiles/Dockerfile.root
    ```

3.  **Replace the `apt-get update` and `apt-get install` block with:**

    ```dockerfile
RUN apt-get update -o Acquire::AllowInsecureRepositories=true -o Acquire::AllowDowngradeToInsecureRepositories=true \
  && apt-get install -yq --allow-unauthenticated \
  zsh \
  curl \
  vim \
  git \
  && apt-get clean
    ```

4.  **Save and exit `nano`** (`Ctrl+X`, `Y`, `Enter`).

### 3.7 Building the ESMFold Docker Image

After resolving space and modifying the Dockerfile:

```bash
docker build -f Dockerfiles/Dockerfile.root -t esmfold-gpu .
```

This process will download dependencies and build the `esmfold-gpu` image. It can take a significant amount of time.

## 4. Running ESMFold Predictions with Docker

1.  **Create a FASTA input file (e.g., `test_sequence.fasta` in `~/esmfold-docker-image`):

    ```bash
echo ">test_protein" > test_sequence.fasta
echo "ACDEFGHIKLMNPQRSTVWY" >> test_sequence.fasta
    ```

2.  **Run the Docker container to perform prediction:**

    ```bash
docker run --gpus all -it --rm -v $(pwd):/app esmfold-gpu -i /app/test_sequence.fasta -o /app/output.pdb
    ```

    *   `--gpus all`: Enables GPU access for ESMFold.
    *   `-it --rm`: Interactive, remove container on exit.
    *   `-v $(pwd):/app`: Mounts current directory to `/app` inside container for input/output.
    *   `-i /app/test_sequence.fasta`: Specifies input FASTA file.
    *   `-o /app/output.pdb`: Specifies output PDB file.

## 5. GATSol Integration (Future Steps)

With ESMFold now successfully running in a Docker container, the next steps involve integrating its predictions into the GATSol pipeline. This might involve:

*   Developing a wrapper script to call the ESMFold Docker container with sequences from GATSol's input.
*   Parsing the generated PDB files and extracting relevant features for GATSol's analysis.
*   Ensuring data transfer and file management between the GATSol environment and the ESMFold Docker container.

This setup provides a stable foundation for further development and integration of protein structure prediction into your solubility analysis workflow.
