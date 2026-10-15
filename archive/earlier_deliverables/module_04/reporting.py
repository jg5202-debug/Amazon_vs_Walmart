# Cell 01: Import Reporting Libraries

import html
import json
import textwrap
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import HTML, Image, display

from module_02.data_management import DatabaseManager, validate_records
from module_03.metrics_analysis import (
    CALCULATION_VERSION, METRIC_SPECS, MetricCalculator, build_stage_summary,
    make_run_signature, read_metric_results, validate_metric_records,
)

# Cell 03: Set Presentation Content and Report Notes

PLOT_SPECS = {
    "sales_growth": {
        "title": "Annual Net Sales Growth",
        "ylabel": "Year-on-year growth (%)",
        "reference": 0,
    },
    "operating_margin": {
        "title": "Operating Margin Based on Segment Net Sales",
        "ylabel": "Operating income / net sales (%)",
        "reference": 0,
    },
    "sales_index": {
        "title": "Net Sales Relative to the Configured Base Year",
        "ylabel": "Sales index (base year = 100)",
        "reference": 100,
    },
}
REPORT_LABELS = {
    "company_name": "Company",
    "segment_name": "Segment",
    "analysis_year": "Analysis year",
    "fiscal_year": "Reported fiscal year",
    "period_start": "Period start",
    "period_end": "Period end",
    "comparison_stage": "Study stage",
    "analysis_years": "Analysis years",
    "record_count": "Annual records",
    "net_sales_usd_m": "Net sales (USD millions)",
    "operating_income_usd_m": "Operating income (USD millions)",
    "sales_growth_pct": "Sales growth (%)",
    "operating_margin_pct": "Operating margin (%)",
    "sales_index": "Sales index",
    "sales_change_from_base_pct": "Sales change from base (%)",
    "margin_change_from_base_pp": "Margin change from base (pp)",
    "source_url": "Official source URL",
    "source_section": "Source section and year columns",
    "accessed_date": "Source access date",
    "date_basis": "Basis for period dates",
    "sales_growth_pct_valid_years": "Growth: valid years",
    "sales_growth_pct_mean": "Growth: annual mean (%)",
    "operating_margin_pct_valid_years": "Margin: valid years",
    "operating_margin_pct_mean": "Margin: annual mean (%)",
    "sales_index_valid_years": "Index: valid years",
    "sales_index_mean": "Index: annual mean",
}
REPORT_NOTES = [
    "2019 supplies a pre-pandemic reference for sales scale and operating margin.",
    "The 2020-2021 and 2022-2024 stages are study groupings, not estimates of pandemic effects or a claim that the pandemic ended in 2022.",
    "This is a small, descriptive segment comparison. One pre-pandemic year cannot establish a pre-pandemic trend or a counterfactual.",
    "Amazon North America includes service revenue and covers a different geography from Walmart U.S.; the segments are not identical retail businesses.",
    "Historical columns in the adopted official reports are used; later restatements are not automatically included.",
    "Changes in these financial indicators alone cannot identify the causes of the observed patterns.",
]
REPORT_STYLE = """
body { margin: 0; color: #253247; background: #fff;
       font: 16px/1.75 Arial, sans-serif; }
main { max-width: 1120px; margin: auto; padding: 38px 28px 70px; }
h1 { font-size: 28px; line-height: 1.4; }
h2 { margin-top: 42px; font-size: 21px; }
a { color: #1d4ed8; }
figure { margin: 24px 0; }
figure img { width: 100%; height: auto; }
figcaption, .meta { color: #566579; font-size: 14px; }
.table-scroll { overflow-x: auto; margin: 18px 0; }
table { border-collapse: collapse; font-size: 13px; width: 100%; }
th, td { text-align: left; border-bottom: 1px solid #dce2e8;
         padding: 9px 11px; vertical-align: top; }
th { background: #f0f4f7; white-space: nowrap; }
td { min-width: 80px; }
.identity { overflow-wrap: anywhere; }
@media print { main { padding: 0; } .table-scroll { overflow: visible; }
               figure { break-inside: avoid; } }
"""

# Cell 04: Define a Verified Database Reader for Reporting

def read_reporting_data(config, database_path):
    database = DatabaseManager(database_path)
    database.connect()
    try:
        database.connection.execute("PRAGMA query_only = ON")
        financial_df = database.read_selected_records(config)
        validate_records(financial_df, config)
        signature = make_run_signature(config, financial_df)
        calculator = MetricCalculator(config)
        expected_df = calculator.build_analysis_frame(financial_df)
        expected_df = calculator.calculate(expected_df)
        saved_df = read_metric_results(database, config, signature)
        validate_metric_records(saved_df, expected_df, config, signature)

        values_by_key = {}
        for row in saved_df.to_dict("records"):
            key = (row["unit_id"], row["analysis_year"], row["metric_name"])
            values_by_key[key] = row["metric_value"]
        rows = []
        for source_row in expected_df.to_dict("records"):
            row = source_row.copy()
            for metric in config.metrics:
                key = (row["unit_id"], row["analysis_year"], metric)
                row[METRIC_SPECS[metric]["column"]] = values_by_key[key]
            rows.append(row)
        report_df = pd.DataFrame(rows)
        return financial_df, report_df, saved_df, signature
    finally:
        database.close()

# Cell 05: Define Comparisons with the Configured Base Year

def build_baseline_comparison(report_df, config):
    rows = []
    for unit in config.business_units:
        selected = report_df[report_df["unit_id"] == unit["unit_id"]]
        base = selected[selected["analysis_year"] == config.index_base_year].iloc[0]
        for source_row in selected.to_dict("records"):
            row = {
                "unit_id": source_row["unit_id"],
                "company_name": source_row["company_name"],
                "segment_name": source_row["segment_name"],
                "analysis_year": source_row["analysis_year"],
                "fiscal_year": source_row["fiscal_year"],
                "net_sales_usd_m": source_row["net_sales_usd_m"],
                "sales_change_from_base_pct": (
                    source_row["net_sales_usd_m"] / base["net_sales_usd_m"] - 1
                ) * 100,
            }
            if "operating_margin" in config.metrics:
                row["operating_margin_pct"] = source_row["operating_margin_pct"]
                row["margin_change_from_base_pp"] = (
                    source_row["operating_margin_pct"] - base["operating_margin_pct"]
                )
            rows.append(row)
    return pd.DataFrame(rows)

# Cell 06: Define the Reusable Report Builder

class ReportBuilder:
    def __init__(self, config, results_directory):
        self.config = config
        self.results_directory = Path(results_directory)
        self.figures_directory = self.results_directory / "figures"

    def create_charts(self, report_df):
        self.figures_directory.mkdir(parents=True, exist_ok=True)
        years = []
        stage_years = {}
        for period in self.config.periods:
            year = period["analysis_year"]
            stage = period["comparison_stage"].strip()
            years.append(year)
            if stage not in stage_years:
                stage_years[stage] = []
            stage_years[stage].append(str(year))
        stage_notes = []
        for stage, stage_list in stage_years.items():
            stage_notes.append(stage + ": " + ", ".join(stage_list))
        files = {}
        for metric in self.config.metrics:
            spec = PLOT_SPECS[metric]
            column = METRIC_SPECS[metric]["column"]
            fig, ax = plt.subplots(figsize=(10, 6))
            for period in self.config.periods:
                stage = period["comparison_stage"].strip()
                stage_number = list(stage_years).index(stage)
                shade = 0.95 if stage_number % 2 == 0 else 0.88
                year = period["analysis_year"]
                ax.axvspan(year - 0.5, year + 0.5, color=str(shade), zorder=0)
            for unit in self.config.business_units:
                selected = report_df[report_df["unit_id"] == unit["unit_id"]]
                selected = selected.sort_values("analysis_year")
                label = unit["ticker"] + " / " + unit["segment_name"]
                ax.plot(selected["analysis_year"], selected[column],
                        marker="o", linewidth=2, label=label)
            ax.axhline(spec["reference"], color="#718096", linestyle="--", linewidth=1)
            ax.axvline(self.config.index_base_year, color="#718096", linestyle=":", linewidth=1)
            ax.set_title(spec["title"], fontsize=14, pad=16)
            ax.set_xlabel("Analysis year (fiscal mapping is approximate)")
            ax.set_ylabel(spec["ylabel"])
            ax.set_xticks(years)
            ax.set_xlim(min(years) - 0.5, max(years) + 0.5)
            ax.grid(axis="y", alpha=0.25)
            ax.legend(fontsize=10)
            fig.subplots_adjust(left=0.10, right=0.97, top=0.88, bottom=0.32)
            caption = "Stage shading: " + " | ".join(stage_notes)
            caption += f". Dotted line: base year {self.config.index_base_year}."
            caption_lines = [textwrap.fill(caption, width=115)]
            caption_lines.append("Source: adopted official filings; selected segment financial records.")
            caption_lines.append(textwrap.fill(self.config.alignment_note, width=115))
            if metric == "sales_growth":
                caption_lines.append("First study-year growth is unavailable; it is not zero.")
            fig.text(0.10, 0.02, "\n".join(caption_lines),
                     fontsize=8, va="bottom", color="#566579")
            png_path = self.figures_directory / (metric + ".png")
            svg_path = self.figures_directory / (metric + ".svg")
            fig.savefig(png_path, dpi=180)
            fig.savefig(svg_path)
            plt.close(fig)
            files[metric] = {"png": png_path, "svg": svg_path}
        return files

    def write_report(self, body, style):
        self.results_directory.mkdir(parents=True, exist_ok=True)
        title = html.escape(self.config.title)
        document = "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        document += "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        document += f"<title>{title}</title><style>{style}</style></head>"
        document += f"<body><main>{body}</main></body></html>"
        path = self.results_directory / "research_report.html"
        path.write_text(document, encoding="utf-8")
        return path

# Cell 07: Define Table Formatting and Descriptive Findings

def format_number(value):
    return f"{value:,.2f}"


def format_report_table(frame):
    view = frame.rename(columns=REPORT_LABELS)
    table = view.to_html(index=False, na_rep="NA", float_format=format_number,
                         border=0, escape=True)
    return "<div class='table-scroll'>" + table + "</div>"


def build_findings(report_df, baseline_df, config):
    findings = []
    last_year = max(report_df["analysis_year"])
    for unit in config.business_units:
        selected = report_df[report_df["unit_id"] == unit["unit_id"]]
        last = selected[selected["analysis_year"] == last_year].iloc[0]
        comparison = baseline_df[
            (baseline_df["unit_id"] == unit["unit_id"])
            & (baseline_df["analysis_year"] == last_year)
        ].iloc[0]
        text = unit["company_name"] + " / " + unit["segment_name"]
        text += f": net sales in analysis year {last_year} were {last['net_sales_usd_m']:,.0f} USD millions."
        text += f" Sales changed by {comparison['sales_change_from_base_pct']:+.2f}% relative to {config.index_base_year}."
        if "operating_margin" in config.metrics:
            text += f" Operating margin was {last['operating_margin_pct']:.2f}%,"
            text += f" a change of {comparison['margin_change_from_base_pp']:+.2f} percentage points from the base year."
            low = selected.sort_values(["operating_margin_pct", "analysis_year"]).iloc[0]
            text += f" The lowest observed annual margin was {low['operating_margin_pct']:.2f}% in analysis year {low['analysis_year']}."
        findings.append(text)
    return findings

# Cell 08: Define the Report Structure

def build_report_body(config, report_df, baseline_df, stage_df, chart_files,
                      findings, notes, signature, generated_time):
    parts = ["<h1>" + html.escape(config.title) + "</h1>"]
    parts.append("<p>" + html.escape(config.research_question) + "</p>")
    parts.append("<p class='meta'>Generated (UTC): " + html.escape(generated_time) + "</p>")
    parts.append("<p class='meta identity'>Input signature: " + html.escape(signature) + "</p>")
    parts.append("<h2>Research design and definitions</h2>")
    parts.append("<p>" + html.escape(config.alignment_note) + "</p>")
    parts.append("<p>Sales growth = (current / previous annual net sales - 1) * 100. "
                 "Operating margin = segment operating income / segment net sales * 100. "
                 "Sales index = current / base-year net sales * 100. "
                 "Percent values are already multiplied by 100. "
                 "First study-year growth is unavailable and is shown as NA, not zero.</p>")
    parts.append(f"<p>The configured reference year is {config.index_base_year}. "
                 "Sales changes from that year are percentages; margin changes are percentage points. "
                 "These cumulative sales changes are not CAGR.</p>")
    parts.append("<h2>Observed results</h2><ul>")
    for finding in findings:
        parts.append("<li>" + html.escape(finding) + "</li>")
    parts.append("</ul><h2>Annual comparison charts</h2>")
    for metric in config.metrics:
        image_path = "figures/" + chart_files[metric]["png"].name
        title = PLOT_SPECS[metric]["title"]
        parts.append("<figure><img src='" + html.escape(image_path, quote=True)
                     + "' alt='" + html.escape(title, quote=True) + "'>"
                     + "<figcaption>" + html.escape(title) + ". "
                     + "Values come from the verified current SQLite metric results.</figcaption></figure>")
    annual_columns = ["company_name", "segment_name", "analysis_year", "fiscal_year",
                      "comparison_stage", "net_sales_usd_m", "operating_income_usd_m"]
    for metric in config.metrics:
        annual_columns.append(METRIC_SPECS[metric]["column"])
    parts.append("<h2>Annual values</h2>")
    parts.append(format_report_table(report_df[annual_columns]))
    parts.append("<h2>Changes relative to the base year</h2>")
    parts.append(format_report_table(baseline_df.drop(columns=["unit_id"])))
    parts.append("<h2>Stage summaries and available years</h2>")
    parts.append("<p>Each stage mean is an unweighted arithmetic mean of available annual values. "
                 "The table reports the number of valid years for each metric. "
                 "These are not pooled margins or compound growth rates. "
                 "The single-year baseline is a reference, not an equal-length comparison group.</p>")
    parts.append(format_report_table(stage_df.drop(columns=["unit_id"])))
    parts.append("<h2>Scope and limitations</h2><ul>")
    for note in notes:
        parts.append("<li>" + html.escape(note) + "</li>")
    for unit in config.business_units:
        for note in unit["scope_notes"]:
            parts.append("<li>" + html.escape(unit["segment_name"] + ": " + note) + "</li>")
    parts.append("</ul><h2>Source and period audit</h2>")
    source_columns = ["company_name", "segment_name", "analysis_year", "fiscal_year",
                      "period_start", "period_end", "source_section", "date_basis", "accessed_date"]
    parts.append(format_report_table(report_df[source_columns]))
    parts.append("<h2>Adopted official report links</h2><ul>")
    for source_url in report_df["source_url"].drop_duplicates():
        safe_url = html.escape(source_url, quote=True)
        parts.append(f"<li class='identity'><a href='{safe_url}'>{safe_url}</a></li>")
    parts.append("</ul><p>Amounts were manually transcribed from free official reports and checked in Module 02. "
                 "The pipeline does not fetch new filings during reporting. Full report HTML snapshots are not bundled.</p>")
    return "\n".join(parts)
