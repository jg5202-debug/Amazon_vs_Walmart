# Retail Comparison Data

This directory contains real, verified segment-year transcriptions and the Module 02 outputs.

- raw/amazon_segment_raw.csv: Amazon North America 2019-2024, six annual records.
- raw/walmart_segment_raw.csv: Walmart U.S. FY2020-FY2025, six annual records.
- raw/source_manifest.json: four adopted official filings, their URLs, table sections and fiscal columns.
- financial_data.csv: combined raw import snapshot, twelve records.
- clean/financial_records.csv: original evidence fields and standardized USD-million numeric measures, twelve records.
- retail_comparison.sqlite: two business units, twelve financial records and an initially empty metric_results table.

See ../module_02/source_notes.md for the official source references and verified figures. Full official HTML snapshots are not bundled; raw/reports/README.md explains their optional acquisition. Period start dates are derived from the annual calendars disclosed in the reports and documented in each row's date_basis.

The database and clean audit file can be rebuilt by running the twelve cells in Module 02. The raw input files are preserved. Re-importing identical records does not create duplicates; updated base records invalidate that segment's saved metrics. No financial ratios have been computed yet.

Actual fiscal years and dates are stored in the base table. The 2019 analysis-year reference and pandemic-stage mapping remain in Module 01's study.json and are joined in Module 03.
