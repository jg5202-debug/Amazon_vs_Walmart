# Retail Growth and Profitability Comparison

The two diagrams are supplied as high-resolution PNG images and SVG vector files. Diagram 1 describes the four-module workflow. Diagram 2 expands it into a concrete source-to-report pipeline, with verified source previews and proposed processing and storage steps. The descriptions below also provide text that can be reused in a diagram-generation tool.

- [Diagram 1: Project Workflow (PNG)](diagrams/01_project_workflow.png)
- [Diagram 1: Project Workflow (SVG)](diagrams/01_project_workflow.svg)
- [Diagram 2: Data Pipeline (PNG)](diagrams/02_data_pipeline.png)
- [Diagram 2: Data Pipeline (SVG)](diagrams/02_data_pipeline.svg)

## Diagram 1: Project Workflow

Create an English project workflow with four modules arranged from top to bottom. Title it "Retail Growth and Profitability Comparison: Project Workflow". Use rounded rectangles for processes, diamonds for validation decisions, and document shapes or labeled rectangles for saved files. Label Module 01 as implemented and Modules 02-04 as planned.

Start with Module 01: Research Configuration. Enter the company segments, analysis years, fiscal-year mapping, selected metrics, index base year, source references, and file paths. Initialize and validate the StudyConfig object. If validation fails, correct the settings and repeat the check. If it passes, save study.json.

Continue to Module 02: Data and Database Management. Collect segment net sales and operating income from free official annual reports. Transcribe the small sample into source-specific CSV files, load them into pandas DataFrames, standardize amounts and dates, and check source provenance, duplicates, required values, and coverage. Correct failed records before writing accepted business-unit and financial records to SQLite.

Continue to Module 03: Metrics and Comparative Analysis. Query the financial records from SQLite, join the configuration's fiscal-year mapping, and calculate sales growth, operating margin, and sales index. Keep missing prior-year growth as NULL and allow negative operating income. Save metric results with the study ID and configuration signature, then compare the selected segments.

Finish with Module 04: Reporting and Workflow. Query the saved results, generate charts and comparison tables, explain the observed patterns using cited annual-report discussions, state the comparability limitations, and export the report. Use the configuration as the input to all later modules. Do not represent the planned database or analysis as already implemented.

## Diagram 2: Data Pipeline and DataFrame Flow

Create a separate English data-flow diagram as the implementation blueprint supporting Diagram 1. Show specific external sources, acquisition tools, in-memory DataFrames, transformation steps, persistent files, database tables, and reporting outputs. Use two parallel source branches, one shared SQLite database, and labeled read/write arrows. Use the exact DataFrame and file names below. All paths are relative to the project root; the JSON configuration resolves them from its own location. Annotate the diagram: "Verified source previews; ingestion, database storage, and calculations are planned."

### Source and acquisition branches

Amazon branch: use the North America rows in Note 10, Segment Information. Use the [2022 Form 10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872423000004/amzn-20221231.htm) for 2020-2021 and the [2024 Form 10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/amzn-20241231.htm) for 2022-2024. The overlapping 2022 column can be cross-checked, but must not create a duplicate annual record. Exclude AWS, International, and consolidated totals.

Walmart branch: use the Walmart U.S. segment table in the Management's Discussion and Analysis and cross-check the segment note. Use the [FY2023 Form 10-K](https://www.sec.gov/Archives/edgar/data/104169/000010416923000020/wmt-20230131.htm) for FY2021-FY2022 and the [FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/104169/000010416925000021/wmt-20250131.htm) for FY2023-FY2025. Cross-check the overlapping FY2023 column. Use segment net sales, not total revenues or comparable-sales growth, for the selected sales measure. Exclude Walmart International, Sam's Club, and consolidated totals.

Tool: a web browser for accessing and saving the official HTML reports. Planned report snapshots are data/raw/reports/amazon_2022_10k.html, amazon_2024_10k.html, walmart_fy2023_10k.html, and walmart_fy2025_10k.html. For this small sample, manually transcribe and verify the selected rows rather than assuming an automatic PDF extractor will identify the correct segment.

Tool: a CSV-capable text editor or spreadsheet editor for the initial transcription. Planned raw files are data/raw/amazon_segment_raw.csv and data/raw/walmart_segment_raw.csv. Preserve the original amount strings, including commas and loss parentheses, plus source URLs and table locations.

### Raw DataFrames

In the PyCharm Jupyter Notebook, use pandas.read_csv with dtype=str to load the two raw CSV files as amazon_raw_df and walmart_raw_df, each containing five segment-year rows. Each row includes unit_id, company_name, segment_name, fiscal_year, period_start, period_end, net_sales_raw, operating_income_raw, reported_currency, reported_unit, source_url, source_section, and accessed_date. Dates and amounts must be taken from the reports, not inferred solely from the company name.

Show verified source values as preview annotations. Amounts below are USD millions, not whole dollars:

- Amazon North America FY2024: net_sales_raw="387,497"; operating_income_raw="24,967". [Source](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/amzn-20241231.htm)
- Walmart U.S. FY2025: net_sales_raw="462,415"; operating_income_raw="23,882". [Source](https://www.sec.gov/Archives/edgar/data/104169/000010416925000021/wmt-20250131.htm)

Combine the frames using pandas.concat to create raw_df with ten rows. Export the combined import record to data/financial_data.csv using DataFrame.to_csv(index=False). Do not overwrite the two source-specific raw files during cleaning.

### Cleaning and validation

Transform raw_df into clean_df. Use ordinary Python string handling to remove thousands separators and convert parentheses to minus signs, followed by pandas.to_numeric. Use pandas.to_datetime for period_start and period_end. Standardize money to USD millions and retain the original strings and units. Use numeric columns net_sales_usd_m and operating_income_usd_m. Keep fiscal_year as an integer and unit_id as the stable segment identifier.

Validate required values, positive net sales, integer fiscal years, start dates before end dates, source references, unique unit_id/fiscal_year pairs, and the exact configured coverage. Negative operating income is valid. Missing or conflicting required values must return to source review; they must not be silently filled with zero or removed. When two reports repeat a year, compare the values and choose the documented report version explicitly.

Accepted clean_df has ten annual rows. Export an audit copy to data/clean/financial_records.csv using DataFrame.to_csv(index=False). Original and standardized values and provenance remain available for checking.

### SQLite persistence

Use a simple DatabaseManager class with Python sqlite3, parameterized statements, and transactions to create and populate data/retail_comparison.sqlite. The proposed tables are business_units, financial_records, and metric_results. Store the two segment definitions in business_units and the ten clean annual records in financial_records. Enforce uniqueness for the adopted segment/fiscal-year record. Do not store a study-specific analysis_year as the permanent financial period; that mapping belongs to the study configuration. The metric_results table is populated later by Module 03.

### Query, alignment, and calculations

Use pandas.read_sql_query with the sqlite3 connection to query the selected annual financial records into financial_df. Convert the ten configured segment/year mappings from study.json into period_map_df with study_id, analysis_year, unit_id, and fiscal_year. Use pandas.merge on unit_id and fiscal_year, validate a one-to-one match, and require every configured row to have matching financial data. The result is analysis_df with ten rows, the fiscal and analysis years, actual report dates, and the two standardized financial measures.

Sort analysis_df by unit_id and analysis_year using DataFrame.sort_values. Use simple functions, for loops, and if checks to calculate three columns in metrics_df: sales_growth_pct=(current net sales / previous net sales - 1)*100; operating_margin_pct=operating income / net sales*100; sales_index=net sales / the same segment's 2020 net sales*100. Never calculate growth across two different segments. Check denominators before division.

metrics_df has ten rows in a wide format. Convert it to metrics_long_df with one row per study, segment, analysis year, and metric. The three metrics create thirty result rows, including two NULL first-year growth values under the current five-year-only input policy. Include study_id, config_signature, unit_id, analysis_year, metric_name, metric_value, value_unit, calculation_time, and missing_reason. Write these results into SQLite metric_results using the same DatabaseManager. A changed configuration or changed source record requires recalculation of affected results.

Optional baseline sales from Amazon 2019 and Walmart FY2020 can support first-year growth in a later extension. They are not included in the default ten formal annual rows or in the source previews shown here.

### Saved-result reporting

Query the saved metric_results for the current study and configuration using pandas.read_sql_query to create report_df. Pivot the long results into a comparison layout when needed. Export results/comparison_metrics.csv with DataFrame.to_csv. Use Matplotlib to produce results/sales_index.png and results/operating_margin.png through savefig. Use the same source references and scope notes to produce results/research_report.md. The report must distinguish descriptive differences from causal claims and retain the approximate fiscal alignment and business-mix limitations.

In the diagram, DataFrames are temporary in-memory objects. CSV, JSON, HTML snapshots, PNG files, Markdown files, and the SQLite file are persistent outputs. The raw data does not originate inside pandas; pandas loads it from the verified source transcription. The reporting stage reads the saved database results, not merely the text printed by a previous Notebook cell.

### Tool references

- [pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html): CSV to DataFrame.
- [pandas.read_sql_query](https://pandas.pydata.org/docs/reference/api/pandas.read_sql_query.html): database query to DataFrame.
- [Python sqlite3](https://docs.python.org/3.13/library/sqlite3.html): database operations.
- [Matplotlib savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html): persistent chart exports.

## Implementation status

Module 01 has code and a detailed Notebook guide. Source table figures used in the diagram previews were verified against the four official filings above. The raw CSV files, saved report snapshots, SQLite database, pandas pipeline, and report outputs named in Diagram 2 are planned destinations and processing steps, not files already created by this diagram-generation task.
