# Module 02: Source Verification Notes

Verified on 2026-10-10. All money amounts in the source tables are USD millions. Net sales and operating income were transcribed, not growth percentages, total revenues or consolidated values.

Amazon covers 2019-2024 and Walmart U.S. covers FY2020-FY2025. The fiscal mapping and pandemic-stage labels come from Module 01, not from the raw financial tables.

## S1: Amazon 2021 Form 10-K

[Official filing](https://www.sec.gov/Archives/edgar/data/1018724/000101872422000005/amzn-20211231.htm)

Table: Note 10 - Segment Information; North America.

- Fiscal 2019: net sales 170,773; operating income 7,033.

- Fiscal 2020: net sales 236,282; operating income 8,651.

- Fiscal 2021: net sales 279,833; operating income 7,271.

## S2: Amazon 2024 Form 10-K

[Official filing](https://www.sec.gov/Archives/edgar/data/1018724/000101872425000004/amzn-20241231.htm)

Table: Note 10 - Segment Information; North America.

- Fiscal 2022: net sales 315,880; operating income (2,847).

- Fiscal 2023: net sales 352,828; operating income 14,877.

- Fiscal 2024: net sales 387,497; operating income 24,967.

## S3: Walmart FY2022 Form 10-K

[Official filing](https://www.sec.gov/Archives/edgar/data/104169/000010416922000012/wmt-20220131.htm)

Table: Item 7 - MD&A; Walmart U.S. Segment.

- Fiscal 2020: net sales 341,004; operating income 17,380.

- Fiscal 2021: net sales 369,963; operating income 19,116.

- Fiscal 2022: net sales 393,247; operating income 21,587.

## S4: Walmart FY2025 Form 10-K

[Official filing](https://www.sec.gov/Archives/edgar/data/104169/000010416925000021/wmt-20250131.htm)

Table: Item 7 - MD&A; Walmart U.S. Segment; checked against segment note.

- Fiscal 2023: net sales 420,553; operating income 20,620.

- Fiscal 2024: net sales 441,817; operating income 22,154.

- Fiscal 2025: net sales 462,415; operating income 23,882.


## Period dates and adopted report versions

The table headers specify annual years ended December 31 for Amazon and January 31 for Walmart. Walmart's Note 1 also describes a January 31 fiscal year-end for U.S. operations. Start dates are explicitly derived from those annual calendars: January 1 for Amazon, and February 1 of the preceding calendar year for Walmart. This derivation is stored in date_basis on each row; start dates are not claimed to be separately quoted table cells.

The figures use the historical columns in the four cited filings. They are not asserted to incorporate any later restatement beyond those adopted versions. Changing the adopted report version requires source review, updated transcriptions and re-import.

Amazon 2022 reports a North America operating loss of (2,847); it is cleaned to -2847, not zero or missing. Walmart FY2025 net sales are 462,415, distinct from total revenues of 465,009. The selected profitability denominator in Module 03 will be segment net sales.

## Local materials and reuse

The raw CSV files retain reported strings, report URLs, section/column references, dates, currency and unit. source_manifest.json summarizes report choices. Full official HTML snapshots are not included; see data/raw/reports/README.md. This is a local, small-sample transcription/import pipeline.

Reuse requires corresponding source data and correct unit IDs, scope, dates and units, not simply changing the displayed company name. Generic cleaning and database code does not contain Amazon- or Walmart-specific year adjustments.
