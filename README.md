# 🔍 Anonymous Repository for ASE Submission: "BINGO! Simple Optimizers Win Big if Problems Collapse to a Few Buckets"

> **Note:** This repository has been anonymized to comply with double-blind review requirements for ASE 2025. All identifying information (author names, institutional references, Git history) has been redacted. Full attribution and licensing will be restored upon acceptance.

---

## 📄 Summary

This repository contains the code, scripts, and data used to reproduce the results from our paper:

> **"BINGO! Simple Optimizers Win Big if Problems Collapse to a Few Buckets"**  
> _Submitted to ASE 2025 (Double-Blind Review)_

We present the **BINGO effect**, a prevalent data compression phenomenon in software engineering (SE) optimization. Leveraging this, we show that **simple optimizers**—`RANDOM`, `LITE`, `LINE`—perform on par with the state-of-the-art `DEHB`, while running up to **10,000× faster**.

---
## 🧪 Experimental Setup

All experiments were run on a 4-core Linux (Ubuntu 24.04) system (1.30GHz, 16GB RAM, no GPU).

### Configuration

- **Datasets**: 39 MOOT tasks in `data/moot/`
- **Repeats**: 20 runs per optimizer
- **Budgets**: {6, 12, 18, 24, 50, 100, 200}
- **Optimizers**: `DEHB`, `LITE`, `LINE`, `RANDOM`
- **Evaluation**:
  - Effectiveness/ Benefit: distance-to-heaven (multi-objective)
  - Cost: no. of accessed labels, wall-clock time
---
## 📊 Reproducing the Results (Table V, Figures 5 & 6)

These instructions reproduce all core results from the paper, including **Table V**, **Figure 5**, and **Figure 6**.

All experiments were run using **Python 3.13**.

---

### ➤ Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

---

### ➤ Step 2: Generate Table V

```bash
cd experiments/LUA_run_all/
make comparez
make report
```

The output will be saved to:

```
results/optimization_performance/report.csv
```

---

### ➤ Step 3: Generate Figure 5 (%Best vs. Label Budget)

```bash
cd experiments/
python3 optim_performance_comp.py
```

---

### ➤ Step 4: Generate Figure 6 (Runtime Comparison)

```bash
cd experiments/
python3 performance.py
```

---

### 🧪 Optional: Re-run Optimizers

We include precomputed results for `DEHB` and `Active_Learning` (LITE) to save time. To regenerate:

```bash
# A. Remove existing results
rm -rf results/results_DEHB results/results_Active_Learning

# B. Generate commands (use NAME=Active_Learning for LITE, NAME=DEHB for DEHB)
make generate-commands NAME=Active_Learning   # or NAME=DEHB

# C. Run the optimizer
cd experiments/
./commands.sh
```

---

## 📦 Repository Structure

```plaintext
.
├── data/                         # Input data directory
│   └── moot/                     # MOOT datasets: 39 SE optimization tasks

├── active_learning/              # Active learning source code
│   ├── LICENSE.md                # Original license (MIT; redacted for double-blind)
│   └── src/
│       └── bl.py                 # Contains Bayesian active learner

├── experiments/                  # Scripts for running experiments and generating plots/tables
│   ├── FileResultsReader.py      # Reads optimizer result files
│   ├── LUA_run_all/              # Lua scripts containing LITE and TABLE V generation logic
│   │   ├── Makefile              # Automates command/script generation
│   │   ├── run_all.lua           # Generates TABLE V
│   │   └── stats.lua             # Scott-Knott/effect size stats logic
│   ├── __init__.py
│   ├── experiement_runner_parallel.py  # Runs DEHB & LITE
│   ├── optim_performance_comp.py       # Script to generate Fig. 5
│   └── performance.py           # Script to generate Fig. 6

├── models/                       # Manages and evaluates configs
│   ├── __init__.py
│   ├── configurations/
│   │   └── model_config_static.py   # Reads and manages tabular configs from MOOT
│   └── model_wrapper_static.py     # Wrapper class for config evaluation

├── optimizers/                   # Optimizers implemented in the paper
│   ├── ActLearnOptimizer.py      # Active learning optimizer (LITE)
│   ├── DEHBOptimizer.py          # DEHB optimizer
│   ├── __init__.py
│   └── base_optimizer.py         # Abstract base class for all optimizers

├── results/                      # Output directories for optimizer runs
│   ├── results_Active_Learning/  # Results from LITE
│   └── results_DEHB/             # Results from DEHB

└── utils/                        # Utility scripts and shared functions
    ├── DistanceUtil.py           # Computes "distance to heaven"
    ├── LoggingUtil.py            # Sets up and manages logging
    ├── __init__.py
    └── data_loader_templated.py  # Loads and parses CSV datasets

├── .gitignore                    # Ignore logs, cache, and other non-reproducible files
├── LICENSE                       # MIT license (temporarily redacted)
├── Makefile                      # Automates command/script generation and execution
├── README.md                     # Artifact overview and reproduction instructions
└── requirements.txt              # Python dependencies for experiments and plotting
```

---

## ⚙️ Optimizers

| Optimizer | Description |
|----------|-------------|
| `RANDOM` | Random sampling of bucketed data |
| `LITE`   | Naive Bayes-based active learner (selects high g/r) |
| `LINE`   | Diversity sampling via KMeans++ |
| `DEHB`   | Differential Evolution + Hyperband |

---

## 🔐 License

> Temporarily redacted for double-blind review. Includes MIT-licensed components. Full license will be restored upon acceptance.

---

## 🔗 External Links

> Will be updated upon acceptance:
- 📜 Paper DOI
- 📁 Dataset DOI
- 🧪 Artifact DOI

---