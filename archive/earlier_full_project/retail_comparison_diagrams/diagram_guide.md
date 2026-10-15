# Retail Growth and Profitability Comparison

The two diagrams are supplied as high-resolution PNG images and SVG vector files. Diagram 1 describes the four-module workflow. Diagram 2 expands it into a concrete source-to-report pipeline, with verified source previews and proposed processing and storage steps. The descriptions below also provide text that can be reused in a diagram-generation tool.

- [Diagram 1: Project Workflow (PNG)](diagrams/01_project_workflow.png)
- [Diagram 1: Project Workflow (SVG)](diagrams/01_project_workflow.svg)
- [Diagram 2: Data Pipeline (PNG)](diagrams/02_data_pipeline.png)
- [Diagram 2: Data Pipeline (SVG)](diagrams/02_data_pipeline.svg)

## Research rationale: a pre-pandemic reference

The inclusion of 2019 provides a pre-pandemic reference for comparing subsequent changes in sales and operating profitability. The study compares Amazon North America in 2019-2024 with Walmart U.S. in FY2020-FY2025, using the configured approximate fiscal alignment. The 2019 analysis year is both a formal observation and the sales-index base year, set to 100 separately for each segment.

Research question: Relative to the 2019 baseline, how did sales growth and operating margins differ between the two segments during 2020-2021 and the subsequent 2022-2024 adjustment period?

- **2019: Pre-pandemic baseline.** Establish the reference sales scale and operating margin.
- **2020-2021: Pandemic disruption.** Describe changes in sales growth and profitability and compare the two segments' paths.
- **2022-2024: Subsequent adjustment.** Describe whether growth and profitability changes persisted, slowed or reversed.

These stages are operational groupings for this project, rather than a claim that the pandemic ended in 2022. Only one pre-pandemic year is included, so pre-pandemic trends cannot be evaluated. Annual, nominal segment data and differences in fiscal dates and business mix support a descriptive comparison, not identification of a causal COVID-19 effect. Retain annual observations and clearly state the method if stage averages are added.

## Diagram 1: Project Workflow

Create an English project workflow with four modules arranged from top to bottom. Title it "Retail Growth and Profitability Comparison: Project Workflow". Use rounded rectangles for processes, diamonds for validation decisions, and document shapes or labeled rectangles for saved files. Label all four modules as implemented.

Start with Module 01: Research Configuration. Enter the company segments, six analysis years, fiscal-year mapping, comparison-stage labels, selected metrics, the 2019 index base year, source references, and file paths. Initialize and validate the StudyConfig object. If validation fails, correct the settings and repeat the check. If it passes, save study.json. Store the optional comparison_stage label inside each period dictionary so that the research content stays separate from the reusable class.

Continue to Module 02: Data and Database Management. Collect segment net sales and operating income from free official annual reports. Transcribe the small sample into source-specific CSV files, load them into pandas DataFrames, standardize amounts and dates, and check source provenance, duplicates, required values, and coverage. Correct failed records before writing accepted business-unit and financial records to SQLite.

Continue to Module 03: Metrics and Comparative Analysis. Query the financial records from SQLite, join the configuration's fiscal-year mapping and comparison-stage labels, and calculate sales growth, operating margin, and sales index. Keep 2019 growth as NULL because 2018 sales are not collected; 2020-2024 growth uses prior-year sales. Allow negative operating income. Save metric results with the study ID and configuration signature, then compare the selected segments and stages relative to 2019.

Finish with Module 04: Reporting and Workflow. Query the saved results, generate charts and comparison tables, mark the 2019 reference and the two later stages, and describe calculated patterns and retain official source links. Compare sales index to the reference value 100 and operating margins to the 2019 level in percentage points. State the comparability and causal-inference limitations, and export the report. Use the configuration as the input to all later modules. Module 04 charts and the HTML report are implemented.

## Diagram 2: Data Pipeline and DataFrame Flow

Create a separate English data-flow diagram as the implementation blueprint supporting Diagram 1. Show specific external sources, acquisition tools, in-memory DataFrames, transformation steps, persistent files, database tables, and reporting outputs. Use two parallel source branches, one shared SQLite database, and labeled read/write arrows. Use the exact DataFrame and file names below. All paths are relative to the project root; the JSON configuration resolves them from its own location. Annotate the diagram: "All four modules implemented: CSV, SQLite, metrics, verified reporting and charts."

### Source and acquisition branches

Amazon branch: use the North America rows in Note 10, Segment Information. Use the [2021 Form 10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872422000005/amzn-20211231.htm) for 2019-2021 and the [2024 Form 10-K](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/amzn-20241231.htm) for 2022-2024. These two selected three-year tables cover the six years without duplicate records. Exclude AWS, International, and consolidated totals.

Walmart branch: use the Walmart U.S. segment table in the Management's Discussion and Analysis and cross-check the segment note. Use the [FY2022 Form 10-K](https://www.sec.gov/Archives/edgar/data/104169/000010416922000012/wmt-20220131.htm) for FY2020-FY2022 and the [FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/104169/000010416925000021/wmt-20250131.htm) for FY2023-FY2025. Use segment net sales, not total revenues or comparable-sales growth, for the selected sales measure. Exclude Walmart International, Sam's Club, and consolidated totals.

Tool: web access for reviewing official reports and verifying selected tables, followed by manual CSV transcription. Official links and adopted columns are saved in data/raw/source_manifest.json and module_02/source_notes.md. Full official HTML snapshots are not bundled. Optional browser-saved snapshots can use data/raw/reports/amazon_2021_10k.html, amazon_2024_10k.html, walmart_fy2022_10k.html, and walmart_fy2025_10k.html. For this small sample, manually transcribe and verify the selected rows rather than assuming an automatic PDF extractor will identify the correct segment.

Tool: CSV-capable editing or ordinary CSV serialization for the initial transcription. The delivered raw files are data/raw/amazon_segment_raw.csv and data/raw/walmart_segment_raw.csv. Preserve the original amount strings, including commas and loss parentheses, plus source URLs and table locations. The reusable Notebook reads these inputs, rather than pretending to scrape segment values automatically.

### Raw DataFrames

In the PyCharm Jupyter Notebook, use pandas.read_csv with dtype=str to load the two raw CSV files as amazon_raw_df and walmart_raw_df, each containing six segment-year rows. Each row includes unit_id, company_name, segment_name, fiscal_year, period_start, period_end, net_sales_raw, operating_income_raw, reported_currency, reported_unit, source_url, source_section, accessed_date, and date_basis. Amounts and annual year-end dates come from report tables. Start dates are explicitly derived from the disclosed annual calendars and documented in date_basis; they are not presented as separately quoted source cells.

Show verified source values as preview annotations. Amounts below are USD millions, not whole dollars:

- Amazon North America FY2024: net_sales_raw="387,497"; operating_income_raw="24,967". [Source](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/amzn-20241231.htm)
- Walmart U.S. FY2025: net_sales_raw="462,415"; operating_income_raw="23,882". [Source](https://www.sec.gov/Archives/edgar/data/104169/000010416925000021/wmt-20250131.htm)
- Amazon North America FY2019 baseline: net_sales_raw="170,773"; operating_income_raw="7,033". [Source](https://www.sec.gov/Archives/edgar/data/1018724/000101872422000005/amzn-20211231.htm)
- Walmart U.S. FY2020, paired with analysis year 2019: net_sales_raw="341,004"; operating_income_raw="17,380". [Source](https://www.sec.gov/Archives/edgar/data/104169/000010416922000012/wmt-20220131.htm)

Combine the frames using pandas.concat to create raw_df with twelve rows. Export the combined import record to data/financial_data.csv using DataFrame.to_csv(index=False). Do not overwrite the two source-specific raw files during cleaning.

### Cleaning and validation

Transform raw_df into clean_df. Use ordinary Python string handling to remove thousands separators and convert parentheses to minus signs, followed by pandas.to_numeric. Use pandas.to_datetime for period_start and period_end. Standardize money to USD millions and retain the original strings and units. Use numeric columns net_sales_usd_m and operating_income_usd_m. Keep fiscal_year as an integer and unit_id as the stable segment identifier.

Validate required values, positive net sales, integer fiscal years, start dates before end dates, source references, unique unit_id/fiscal_year pairs, and the exact configured coverage. Negative operating income is valid. Missing or conflicting required values must return to source review; they must not be silently filled with zero or removed. When two reports repeat a year, compare the values and choose the documented report version explicitly.

Accepted clean_df has twelve annual rows. Export an audit copy to data/clean/financial_records.csv using DataFrame.to_csv(index=False). Original and standardized values and provenance remain available for checking.

### SQLite persistence

Use a simple DatabaseManager class with Python sqlite3, parameterized statements, and transactions to create and populate data/retail_comparison.sqlite. The proposed tables are business_units, financial_records, and metric_results. Store the two segment definitions in business_units and the twelve clean annual records in financial_records. Enforce uniqueness for the adopted segment/fiscal-year record. Do not store a study-specific analysis_year or comparison_stage as the permanent financial period; those mappings belong to the study configuration. Module 03 now populates metric_results with the current input signature.

### Query, alignment, and calculations

Query selected financial records into financial_df with pandas.read_sql_query through DatabaseManager. MetricCalculator.build_analysis_frame uses a plain dictionary keyed by unit_id and fiscal_year to apply the configured periods. Validate the selected source coverage before mapping; require a nonempty comparison_stage for each period. It adds analysis_year and comparison_stage to create analysis_df with twelve rows and eighteen columns. No separate period_map_df or pandas.merge is created in the implemented version. Retain actual report dates and source fields.

MetricCalculator.calculate sorts by unit_id and analysis_year and uses plain for loops and if statements. It returns analysis_df with twelve rows and twenty-two columns, including previous_sales_usd_m and the three metric columns: sales_growth_pct=(sales/previous sales-1)*100, operating_margin_pct=income/sales*100, sales_index=sales/base sales*100. Read config.index_base_year, currently 2019, rather than hard-code it. Previous sales resets for each unit, not at stage boundaries. Module 02 source validation requires positive finite sales.

MetricCalculator.to_metric_records expands analysis_df into metric_df with thirty-six rows and nine columns, including two missing 2019 growth values. make_run_signature covers the configuration, selected sources and calculation version. save_metric_results uses the existing database connection and parameterized SQL to replace this study/signature in one transaction; None is stored as SQL NULL. read_metric_results returns stored_metric_df, validated and compared field by field. build_stage_summary returns stage_summary_df with six rows, unweighted means and valid-year counts. Export annual_metrics.csv, metric_records.csv, stage_summary.csv and analysis_manifest.json under results/. Other signature versions may remain, but current queries select the correct signature.

2019 is now a formal comparison year, not an optional auxiliary record. Optional 2018 sales could support 2019 growth in a later extension, but they are not part of this study's current twelve input records. The index reference of 100 must not be confused with a zero growth rate.

### Saved-result reporting (implemented)

Module 04 read_reporting_data uses DatabaseManager to query current financial_df, computes the current input signature and creates expected_df with MetricCalculator only to validate persisted metrics. read_metric_results returns saved_df, exposed as report_metric_df, with 36 current-signature rows. It must pass validate_metric_records. A values_by_key dictionary maps (unit_id, analysis_year, metric_name) to the actual SQL value. These saved values populate report_df (12 x 22), retaining source fields. The query connection is query_only and closes in finally. No metrics are written during reporting.

build_baseline_comparison creates baseline_comparison_df (12 x 9), with net sales changes from the configured reference as cumulative percentages and operating-margin differences as percentage points. build_stage_summary creates report_stage_df (6 x 12), retaining the number of valid years beside each unweighted annual mean. build_findings describes endpoint sales, margins, baseline changes and lowest observed annual margins. It does not invent causal explanations.

ReportBuilder.create_charts uses Matplotlib subplots, plot, axvspan, axhline, axvline and savefig. It exports results/figures/sales_growth.png, operating_margin.png and sales_index.png, each with a corresponding SVG. Stage shading follows study.json and a dotted vertical line marks the configured base year. First-year growth is missing; negative operating margins are retained. Saved captions include source and approximate fiscal alignment.

DataFrame.to_html formats the annual, baseline, stage and source-audit tables for results/research_report.html. Path.write_text persists the complete report; it references PNG files under the sibling figures/ directory. json.dump saves results/report_manifest.json with the input signature, calculation version, report time, complete study configuration, research notes and file index. IPython HTML/Image/display previews tables and saved images inside the Notebook. No additional comparison_metrics.csv or research_report.md is generated; existing Module 03 CSV files remain available.

DataFrames are temporary in-memory objects; the SQLite database, CSV/JSON files, PNG/SVG charts and HTML report persist. Raw data originates in the verified official-report transcription, and reporting reads saved database results. Share the HTML together with its figures folder. The current total Notebook has 44 code cells, sequentially covering all four modules.

### Tool references

- [pandas.read_csv](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html): CSV to DataFrame.
- [pandas.read_sql_query](https://pandas.pydata.org/docs/reference/api/pandas.read_sql_query.html): database query to DataFrame.
- [Python sqlite3](https://docs.python.org/3.13/library/sqlite3.html): database operations.
- [Matplotlib savefig](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.savefig.html): persistent chart exports.

## Implementation status

All four modules have code and detailed Notebook guides. The current project database has two business-unit definitions, twelve financial records and thirty-six current metric results, including two SQL NULL growth values. Annual, long-metric and stage-summary CSV outputs and a run manifest are generated. Full official HTML snapshots are not included; official URLs, table locations, adopted values and a source manifest remain available. All four modules are implemented. Three PNG/SVG charts and a report with four tables and official-source links are available. See module_04/README.md and verification.txt for execution details.
