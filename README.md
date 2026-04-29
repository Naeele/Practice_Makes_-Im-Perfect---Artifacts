# Practice Makes (Im)Perfect: Artifacts

This artifact accompanies the paper:

**_“Practice Makes (Im)Perfect: A Look Back at Benchmarking Practices for Microarchitectural Side-Channel Attacks.”_**

Its purpose is to enable readers to reproduce the results presented in the paper.

In particular, this repository provides the code and data used to generate Figures **1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 and 17**.

Figures **2 and 3** are based on external analysis and are provided separately as html files.

## Running and Editing the Notebooks

To explore or modify the analyses, you can use **Marimo**, an interactive notebook environment.

### Installation
```bash
pip install marimo
pip install uv
```
Documentation: https://docs.marimo.io/getting_started/installation/

### Usage

After installation, run:
```bash
marimo edit artifacts.py
```

> **Note:** The code is designed for clarity and reproducibility rather than maximum performance.

---

**Data Files**

The raw data collected through our survey forms is provided in two CSV files:

- ```form_flaws.csv``` – Contains data regarding all identified benchmarking flaws per paper.

- ```form_data.csv``` – Contains metadata and survey results for the entire paper corpus.

These files serve as the primary input for all analyses reproduced in this artifact.
