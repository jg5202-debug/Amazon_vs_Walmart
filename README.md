# Amazon vs Walmart

This folder contains the retail growth and operating profitability project for
Amazon North America and Walmart U.S., using the 2019-2024 analysis window.

## Current project

- `retail_growth_and_profitability_comparison.ipynb`: the four-module notebook.
- `config.json`: study choices, chart settings, source references and business context.
- `financial_data.csv`: the twelve raw financial records.
- `retail_growth_and_profitability_report.pdf`: the final four-page report.
- `retail_simple_output/`: generated CSV tables, SQLite database, three PNG charts
  and the HTML report. Keep the HTML report and its images together.
- `requirements.txt`: Python packages used by the notebook.
- `docs/`: source feedback document, when available.

## Run

Open the current notebook and run the cells in order. Use the existing Python
environment from the parent JupyterProject folder. The working directory may be
this folder or its parent. If it is somewhere else, set PROJECT_DIRECTORY in
Module 01 Cell 03 to this folder. No new virtual environment is required.

All generated outputs are saved inside `retail_simple_output/` here. Rerunning
replaces those generated outputs. The notebook regenerates the HTML report; the
PDF is a separate final artifact.

## Earlier material

`archive/` preserves the earlier local files, module guides, workflow diagrams,
project packages and previous versions. Those guides describe earlier code;
they are reference material and are not required to run the current notebook.
Use config.json and financial_data.csv in this folder for the current project.
