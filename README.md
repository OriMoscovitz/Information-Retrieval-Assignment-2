# Information Retrieval System - Assignment 2

This repository contains the implementation of the second assignment in the Information Retrieval course (NPFL103).
The system is implemented in Python using Elasticsearch as the underlying retrieval engine.

The project evaluates multiple preprocessing techniques, ranking models, and query construction strategies for both English and Czech document collections.

The experiments include:

- Improved tokenization
- Stop-word removal
- Lemmatization
- Stemming
- Equivalence classes (synonyms)
- DFR weighting
- BM25 ranking
- Pseudo Relevance Feedback (PRF)
- Extended query construction

---
## 📋 Table of Contents

- [🛠️ Setup](#️-setup)
  - [1. Clone the repository](#1-clone-the-repository)
  - [2. Install dependencies](#2-install-dependencies)
  - [3. Install Elasticsearch](#3-install-elasticsearch)
  - [4. Directory structure](#4-directory-structure)
- [▶️ Running the System](#️-running-the-system)
  - [Run-0: Baseline](#run-0-baseline-elasticsearch-configuration)
  - [Run-1: Final Constrained System](#run-1-final-constrained-system)
  - [Run-2: Final Unconstrained System](#run-2-final-unconstrained-system)
- [🧪 Reproducing Intermediate Experiments](#-reproducing-intermediate-experiments)
  - [Experiment 1 - Baseline (Smart Tokenizer)](#experiment-1---baseline-smart-tokenizer)
  - [Experiment 2 - Stop-word Removal](#experiment-2---stop-word-removal)
  - [Experiment 3 - Lemmatization](#experiment-3---lemmatization)
  - [Experiment 4 - Stemming](#experiment-4---stemming-english-only)
  - [Experiment 5/4 - Equivalence Classes](#experiment-5-english--4-czech---equivalence-classes)
  - [Experiment 6/5 - DFR Weighting](#experiment-6-english--5-czech---dfr-weighting)
  - [Experiment 7/6 - BM25 Weighting](#experiment-7-english--6-czech---bm25-weighting)
  - [Experiment 8/7 - Pseudo-Relevance Feedback](#experiment-8-english--7-czech---pseudo-relevance-feedback-prf)
  - [Experiment 9/8 - Title + Description](#experiment-9-english--8-czech---query-construction-title--description)
  - [Experiment 10/9 - Title + Description + Narrative](#experiment-10-english--9-czech---query-construction-title--description--narrative)
- [📊 Evaluation & Plots](#-evaluation--plots)
  - [Results (English)](#results-english)
  - [Results (Czech)](#results-czech)
  - [11-Point Precision-Recall Curves](#11-point-precision-recall-curves)
- [🗂️ System Overview](#️-system-overview)

---

## 🛠️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/OriMoscovitz/Information-Retrieval-Assignment-2.git
cd Information-Retrieval-Assignment-2
```
### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> The Czech pipeline requires **MorphoDiTa** (`ufal.morphodita`) and the model file placed at:
> `morfflex/czech-morfflex2.0-pdtc1.0-220710.tagger`

### 3. Install Elasticsearch
The system requires a running Elasticsearch instance.

Recommended version:
- Elasticsearch 8.x

Run Elasticsearch locally:
```bash
cd assignment2/elasticsearch-9.3.3
./bin/elasticsearch
curl http://localhost:9200
```


### 4. Directory structure

Ensure the following layout under `A1/`:

```
A1/
├── documents_en/          # English XML documents
├── documents_cs/          # Czech XML documents
├── documents_en.lst       # List of English document filenames
├── documents_cs.lst       # List of Czech document filenames
├── topics-train_en.xml
├── topics-test_en.xml
├── topics-train_cs.xml
├── topics-test_cs.xml
├── qrels-train_en.txt
├── qrels-train_cs.txt
└── trec_eval-9.0.7/
    └── trec_eval
outputs/                   # Results are written here
```

---

## ▶️ Running the System

### Run-0: Baseline Elasticsearch configuration
- Pattern tokenizer
- No stop-word removal
- No stemming or lemmatization
- Cosine similarity over term vectors

**English**
```bash
python3 run.py -q topics-train_en.xml -d documents_en.lst -r 0 -o run-0_train_en.res
```

**Czech**
```bash

python3 run.py -q topics-train_cs.xml -d documents_cs.lst -r 0 -o run-0_train_cs.res
```

---

### Run-1: Final Constrained System

Final constrained configuration:
- Lemmatization
- Stop-word removal
- Stemming
- BM25 ranking

**English**
```bash
python3 run.py -q topics-train_en.xml -d documents_en.lst -r 1 -o run-1_train_en.res
```

**Czech**
```bash
python3 run.py -q topics-train_cs.xml -d documents_cs.lst -r 1 -o run-1_train_cs.res
```

---


### Run-2: Final Unconstrained System

- BM25 ranking
- Query expansion using:
- title + description

**English**
```bash
python3 run.py -q topics-train_en.xml -d documents_en.lst -r 2 -o run-2_train_en.res
```

**Czech**
```bash
python3 run.py -q topics-train_cs.xml -d documents_cs.lst -r 2 -o run-2_train_cs.res
```

---

## 🧪 Reproducing Intermediate Experiments

The run-1 and run-2 pipelines went through several iterations. To reproduce intermediate steps, manual code changes are needed as described below.

### Experiment 1 - Baseline (Smart Tokenizer)

**`file_handler.py`: `query_constructor_raw()` and `parse_all_docs()`**

Comment out the lemmatized version and uncomment the raw title:

```python
# for runs 1 and 2
queries[qid] = title

# # for run 3+
# queries[qid] = lemmatize_text(title, lang)
```

**`elastic_handler.py`: `create_index()`**

Set the index configuration to:

```python
body = run1_smart_tokenizer(lang)
```

---

### Experiment 2 - Stop-word Removal

Keep the unlemmatized query setup from Experiment 1, and only change the index configuration in **`elastic_handler.py`: `create_index()`**:

```python
body = run1_stopwords_body(lang)
```

---

### Experiment 3 - Lemmatization

**`file_handler.py`: `query_constructor_raw()` and `parse_all_docs()`**

Revert to the lemmatized version (undo the change from Experiment 1):

```python
# # for runs 1 and 2
# queries[qid] = title

# for run 3+
queries[qid] = lemmatize_text(title, lang)
```

**`elastic_handler.py`: `create_index()`**

Set the index configuration to:

```python
body = run1_lemmatization_body(lang)
```

---

### Experiment 4 - Stemming *(English only)*

Keep the lemmatized query setup from Experiment 3, and only change the index configuration in **`elastic_handler.py`: `create_index()`**:

```python
body = run1_stemming_body(lang)
```

---

### Experiment 5 (English) / 4 (Czech) - Equivalence Classes

Only change the index configuration in **`elastic_handler.py`: `create_index()`**:

```python
body = run1_equivalence_body(lang)
```

---

### Experiment 6 (English) / 5 (Czech) - DFR Weighting

Only change the index configuration in **`elastic_handler.py`: `create_index()`**:

```python
body = run1_dfr_body(lang)
```

---

### Experiment 7 (English) / 6 (Czech) - BM25 Weighting

Only change the index configuration in **`elastic_handler.py`: `create_index()`**:

```python
body = run1_bm25_body(lang)
```

---

### Experiment 8 (English) / 7 (Czech) - Pseudo-Relevance Feedback (PRF)

**`elastic_handler.py`**

Comment out the non-PRF search and uncomment the PRF version:

```python
# # without PRF
# results[qid] = search_query_run1(
#     es=es,
#     index=index,
#     query_text=query_text,
#     top_k=top_k
# )

# with PRF
print(f"------ running PRF ------")
results[qid] = search_query_run1_prf(
    es=es,
    index=index,
    query_text=query_text,
    top_k=top_k
)
```

---

### Experiment 9 (English) / 8 (Czech) - Query Construction: Title + Description

**`elastic_handler.py`**

Revert to the non-PRF version (undo the change from the previous experiment):

```python
# without PRF
results[qid] = search_query_run1(
    es=es,
    index=index,
    query_text=query_text,
    top_k=top_k
)
```

This experiment uses run-2, which by default builds queries from title + description — no further changes are needed.

---

### Experiment 10 (English) / 9 (Czech) - Query Construction: Title + Description + Narrative

**`utils.py`: `run()`**

Change the unconstrained query constructor from title+description to the full data version:

```python
# unconstrained
elif run == 2:
    queries = query_constructor_all_data(lang, train, queries_path)
```

---
## 📊 Evaluation & Plots

To evaluate runs against training qrels and generate MAP / P@10 plots and the 11-point precision-recall curves, run:

```bash
python3 plot_handler.py
```

This reads all `.res` files from `outputs/` and produces `results_english.png` and `results_czech.png`.

To generate the 11-point precision-recall curves, you first need to run the relevant experiment to produce a .res file, then use trec_eval to extract the interpolated precision values at each recall level.

#### Step 1 - Run trec_eval and extract iprec values

After running an experiment, evaluate it with trec_eval and save the iprec_at_recall_* lines to a file:
```bash
./A1/trec_eval-9.0.7/trec_eval A1/qrels-train_en.txt outputs/run-1_train_en.res \
  | grep iprec_at_recall > iprec_run1_en.txt
 ```

The output file should look like:
```bash
iprec_at_recall_0.00    all     0.1765
iprec_at_recall_0.10    all     0.1570
iprec_at_recall_0.20    all     0.0969
iprec_at_recall_0.30    all     0.0729
iprec_at_recall_0.40    all     0.0677
iprec_at_recall_0.50    all     0.0566
iprec_at_recall_0.60    all     0.0330
iprec_at_recall_0.70    all     0.0069
iprec_at_recall_0.80    all     0.0041
iprec_at_recall_0.90    all     0.0021
iprec_at_recall_1.00    all     0.0021
 ```

Repeat this for both the English and Czech result files of the same run.

#### Step 2 - Plot the curves

Once you have both `iprec` files, call:
```bash
plot_iprec_curves(run, eng_file, cze_file)
 ```
where run is the run number (e.g. 0, 1, 2) and eng_file / cze_file are the paths to the saved iprec files for English and Czech respectively. 

For example:
```bash
plot_iprec_curves(1, "iprec_run1_en.txt", "iprec_run1_cs.txt")
 ```

### Results (English)
![English](results_english.png)

* **step 0**: Baseline (run-0)
* **step 1**: Smart tokenizer
* **step 2**: Stop-word removal
* **step 3**: Lemmatization
* **step 4**: Stemming
* **step 5**: Equivalence classes
* **step 6**: DFR weighting
* **step 7**: BM25 weighting
* **step 8**: BM25 + PRF
* **step 9**: Query construction: title + description
* **step 10**: Query construction: title + description + narrative

### Results (Czech)
![Czech](results_czech.png)

* **step 0**: Baseline (run-0)
* **step 1**: Smart tokenizer
* **step 2**: Stop-word removal
* **step 3**: Lemmatization
* **step 4**: Equivalence classes
* **step 5**: DFR weighting
* **step 6**: BM25 weighting
* **step 7**: BM25 + PRF
* **step 8**: Query construction: title + description
* **step 9**: Query construction: title + description + narrative

---

### 11-Point Precision-Recall Curves

#### Run-0 (Baseline)
![11P AP Run-0](11P_AP_results_0.png)

#### Run-1 (Constrained)
![11P AP Run-1](11P_AP_results_1.png)

#### Run-2 (Unconstrained)
![11P AP Run-2](11P_AP_results_2.png)

---
## 🗂️ System Overview

## 🗂️ System Overview

| Component | Description |
|---|---|
| `run.py` | Entry point: parses CLI arguments and dispatches to `utils.run()` |
| `utils.py` | Document loading, query construction, result writing, and run orchestration |
| `file_handler.py` | Document parsing, tokenization, stopword removal, stemming, lemmatization |
| `elastic_handler.py` | Elasticsearch index creation, document indexing, query search, and PRF |
| `elastic_configs.py` | Elasticsearch index body configurations for each experimental step |
| `xml_handler.py` | XML cleaning and extraction utilities |
| `plot_handler.py` | Calls `trec_eval` and plots MAP / P@10 and 11-point precision-recall curves across runs |
