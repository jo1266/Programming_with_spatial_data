# SDS210 – Programming with Spatial Data

This repository contains all **exercises, practicals, and selected solutions** for the course:

**SDS210 – Programming with Spatial Data**
University of Zurich (UZH)
Module Coordinator: Hendrik Wulf

The materials are provided in **Jupyter Notebook format (`.ipynb`)** and are updated weekly throughout the semester.

---

## Course Website (Jupyter Book)

The structured course materials, lecture content, and setup instructions are available here:

**Course Website:**
[https://hendrikwulf.github.io/sds210-jb/](https://hendrikwulf.github.io/sds210-jb/)

The website explains:

* course structure and learning objectives
* setup instructions (Conda, VS Code, Git, Colab, Docker)
* weekly topics and practicals

This repository complements the website with executable notebooks.

---

## Repository Structure

The repository is organised by lesson:

```
L01/
L02/
L03/
...
environment.yml
```

Each lesson folder contains:

* practical notebooks
* exercises
* occasionally solution versions

New notebooks are added weekly.

---

## Getting Started (Recommended: Conda + JupyterLab)

### Download the repository

Download the latest ZIP version:

  [https://gitlab.com/HendrikWulf/sds210/-/archive/main/sds210-main.zip](https://gitlab.com/HendrikWulf/sds210/-/archive/main/sds210-main.zip)

Extract it to a suitable location on your computer.

---

### Install Miniconda (if not yet installed)

Download and install:

  [https://www.anaconda.com/docs/getting-started/miniconda/install](https://www.anaconda.com/docs/getting-started/miniconda/install)

Follow the setup instructions described on the course website:
[https://hendrikwulf.github.io/sds210-jb/book/setup/conda/](https://hendrikwulf.github.io/sds210-jb/book/setup/conda/)

---

### Create the course environment

Open:

* **Anaconda Prompt** (Windows)
* **Terminal** (Mac/Linux)

Then run:

```bash
# Update conda (recommended)
conda update -n base -c defaults conda

# Navigate to the extracted repository folder
cd <path-to-sds210-folder>

# Create the environment (only once)
conda env create -f environment.yml

# Activate the environment
conda activate sds210

# Start JupyterLab
jupyter lab
```

JupyterLab will open in your browser.
You can now open and run any `.ipynb` notebook.

---

### Starting and Ending JupyterLab 

Once your environment exisits, your typical workflow is very simple.

#### Start a Session

Open your terminal and run:

```bash
# Navigate to your repository folder
cd <path-to-sds210>

# Activate the environment
conda activate sds210

# Start JupyterLab
jupyter lab
```

That’s it.

---

#### End a Session

1. Stop JupyterLab in the terminal:

```
Ctrl + C
```

Confirm with:

```
y
```

2. Deactivate the environment:

```bash
conda deactivate
```

---

#### The Workflow

```
cd → activate → jupyter lab → work → Ctrl+C → deactivate
```

Once this becomes routine, working with environments will feel completely natural.

---

## Keeping Your Repository Updated

Since new notebooks are added weekly, you should update regularly.

### Option A 

1. Download the latest ZIP
2. Replace your local folder
3. Keep your own work in a **separate folder** to avoid overwriting

### Option B

Clone the repository via Git (once):

```bash
git clone https://gitlab.com/HendrikWulf/sds210.git
```

Then regularly update via:

```bash
git pull
```

Git instructions are available here:
[https://hendrikwulf.github.io/sds210-jb/book/setup/git/](https://hendrikwulf.github.io/sds210-jb/book/setup/git/)

