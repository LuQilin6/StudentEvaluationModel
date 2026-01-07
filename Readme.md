# Student Application Evaluation System

This repository hosts a pipeline designed to automate the review, scoring, and analysis of student applications. It utilizes Large Language Models (LLMs) for qualitative evaluation and OCR technologies for digitizing application documents.

## Prerequisites

### 1. Installation

Ensure all dependencies are installed. System-level dependencies for PDF processing (Poppler) and OCR (Tesseract) may also be required depending on your OS.

```bash
pip install -r requirements.txt

```

### 2. Configuration

Before running the evaluation pipeline, you must configure the necessary API keys:

* 
**LLM Service:** Open `read_and_analyze_application.ipynb` and insert your OpenAI API key and endpoint URL in the request configuration section.


* **OCR Service:** Open `utils.py` and input your Baidu OCR `API_KEY` and `SECRET_KEY` to enable text extraction from scanned transcripts.

---

## Workflow

### Step 1: Data Processing and Evaluation

**File:** `read_and_analyze_application.ipynb`

This notebook serves as the primary engine for the evaluation process. It performs the following operations:

1. 
**Data Ingestion:** Reads student metadata from Excel files and raw PDF applications.


2. 
**OCR Extraction:** Utilizes functions from `utils.py` to extract text from scanned images or transcripts.


3. 
**LLM Scoring:** Sends parsed profiles to the LLM to generate scores for criteria such as GPA, Math Ability, and Research Potential, along with a "Pass/Fail" recommendation.


4. 
**Export:** Consolidates all evaluations into a structured CSV file (`summary.csv`).



**Usage Instructions:**

1. Open the notebook.
2. Update the `file_path` variables to point to your specific student data folders.
3. Run all cells to process the applications and generate the results.

### Step 2: Statistical Analysis

**File:** `analyze_csv.ipynb`

This notebook processes the CSV output from Step 1 to provide statistical insights and visualizations.

* **Analysis:** Computes descriptive statistics (mean, standard deviation) and pass rates.
* **Visualization:** Generates boxplots, histograms, and heatmaps to correlate specific criteria (e.g., English mastery) with admission outcomes.
* **Validation:** If ground-truth data is available, it calculates model accuracy and recall.

**Usage Instructions:**

1. Ensure the `summary.csv` file exists in the expected directory.
2. Run the notebook cells to generate analytics reports and figures.

---

## File Overview

* 
**`read_and_analyze_application.ipynb`**: The main pipeline for reading PDFs, executing OCR, and querying the LLM.


* **`analyze_csv.ipynb`**: Tools for visualizing and auditing the evaluation results.
* **`utils.py`**: A utility library containing helper functions for PDF parsing (`pdfplumber`), image deskewing, and API calls to OCR services.
* **`requirements.txt`**: The list of Python package dependencies.

> **Note:** Other files present in the repository (e.g., `main.py`, `language_models.py`, `conversers.py`) are components of a separate adversarial testing framework and are not required for the standard student evaluation workflow.