"""Calculate configured annual retail metrics and persist verified results."""

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


CALCULATION_VERSION = "1.0"
METRIC_SPECS = {
    "sales_growth": {"column": "sales_growth_pct", "unit": "percent"},
    "operating_margin": {"column": "operating_margin_pct", "unit": "percent"},
    "sales_index": {"column": "sales_index", "unit": "index_points"},
}
METRIC_COLUMNS = [
    "study_id", "config_signature", "unit_id", "analysis_year", "metric_name",
    "metric_value", "value_unit", "calculation_time", "missing_reason",
]


def make_run_signature(config, financial_df):
    """Identify the settings, calculation version and selected source records."""
    records = financial_df.sort_values(["unit_id", "fiscal_year"]).to_dict("records")
    payload = {
        "calculation_version": CALCULATION_VERSION,
        "settings": config.to_dict(),
        "financial_records": records,
    }
    text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class MetricCalculator:
    """Keep study settings while using the same formulas for every business unit."""

    def __init__(self, config):
        self.config = config

    def build_analysis_frame(self, financial_df):
        records_by_key = {}
        for row in financial_df.to_dict("records"):
            records_by_key[(row["unit_id"], row["fiscal_year"])] = row
        rows = []
        for period in self.config.periods:
            stage = period.get("comparison_stage")
            if not isinstance(stage, str) or not stage.strip():
                raise ValueError("Every analysis period needs a comparison_stage label.")
            for unit in self.config.business_units:
                key = (unit["unit_id"], period["fiscal_years"][unit["unit_id"]])
                row = records_by_key[key].copy()
                row["analysis_year"] = period["analysis_year"]
                row["comparison_stage"] = stage.strip()
                rows.append(row)
        return pd.DataFrame(rows).sort_values(["unit_id", "analysis_year"]).reset_index(drop=True)

    def calculate(self, analysis_df):
        rows = []
        for unit in self.config.business_units:
            unit_df = analysis_df[analysis_df["unit_id"] == unit["unit_id"]]
            unit_df = unit_df.sort_values("analysis_year")
            base_rows = unit_df[unit_df["analysis_year"] == self.config.index_base_year]
            if len(base_rows) != 1:
                raise ValueError(f"Exactly one base-year record is required: {unit['unit_id']}")
            base_sales = float(base_rows.iloc[0]["net_sales_usd_m"])
            previous_sales = None
            for source_row in unit_df.to_dict("records"):
                row = source_row.copy()
                sales = float(row["net_sales_usd_m"])
                income = float(row["operating_income_usd_m"])
                row["previous_sales_usd_m"] = previous_sales
                for metric in self.config.metrics:
                    column = METRIC_SPECS[metric]["column"]
                    if metric == "sales_growth":
                        if previous_sales is None:
                            value = None
                        else:
                            value = (sales / previous_sales - 1) * 100
                    elif metric == "operating_margin":
                        value = income / sales * 100
                    elif metric == "sales_index":
                        value = sales / base_sales * 100
                    row[column] = value
                rows.append(row)
                previous_sales = sales
        return pd.DataFrame(rows).sort_values(["unit_id", "analysis_year"]).reset_index(drop=True)

    def to_metric_records(self, analysis_df, signature, calculation_time):
        records = []
        for row in analysis_df.to_dict("records"):
            for metric in self.config.metrics:
                spec = METRIC_SPECS[metric]
                value = row[spec["column"]]
                reason = None
                if pd.isna(value):
                    value = None
                    reason = "No previous analysis-year record in the study."
                else:
                    value = float(value)
                record = {
                    "study_id": self.config.study_id,
                    "config_signature": signature,
                    "unit_id": row["unit_id"],
                    "analysis_year": row["analysis_year"],
                    "metric_name": metric,
                    "metric_value": value,
                    "value_unit": spec["unit"],
                    "calculation_time": calculation_time,
                    "missing_reason": reason,
                }
                records.append(record)
        return pd.DataFrame(records, columns=METRIC_COLUMNS)


def validate_metric_records(metric_df, analysis_df, config, signature):
    """Check exact metric coverage, missing growth and base-year indexes."""
    expected_keys = set()
    expected_values = {}
    first_year = config.periods[0]["analysis_year"]
    for row in analysis_df.to_dict("records"):
        for metric in config.metrics:
            key = (row["unit_id"], row["analysis_year"], metric)
            expected_keys.add(key)
            expected_values[key] = row[METRIC_SPECS[metric]["column"]]
    if metric_df.duplicated(["unit_id", "analysis_year", "metric_name"]).any():
        raise ValueError("Duplicate metric records were found.")
    actual_keys = set()
    for row in metric_df.to_dict("records"):
        key = (row["unit_id"], row["analysis_year"], row["metric_name"])
        actual_keys.add(key)
        if key not in expected_values:
            raise ValueError(f"Unexpected metric record: {key}")
        metric = row["metric_name"]
        if row["study_id"] != config.study_id or row["config_signature"] != signature:
            raise ValueError(f"Metric run identity does not match: {key}")
        if row["value_unit"] != METRIC_SPECS[metric]["unit"]:
            raise ValueError(f"Metric unit does not match: {key}")
        if not str(row["calculation_time"]).strip():
            raise ValueError(f"Missing calculation time: {key}")
        value = row["metric_value"]
        expected = expected_values[key]
        if metric == "sales_growth" and row["analysis_year"] == first_year:
            if not pd.isna(value) or pd.isna(row["missing_reason"]):
                raise ValueError(f"First-year growth must be missing with a reason: {key}")
        else:
            if pd.isna(value) or not math.isfinite(float(value)):
                raise ValueError(f"A finite metric value is required: {key}")
            if not pd.isna(row["missing_reason"]):
                raise ValueError(f"Available metric must not have a missing reason: {key}")
            if pd.isna(expected) or not math.isclose(float(value), float(expected), rel_tol=1e-12, abs_tol=1e-10):
                raise ValueError(f"Metric value does not match annual calculations: {key}")
        if metric == "sales_index" and row["analysis_year"] == config.index_base_year:
            if not math.isclose(float(value), 100.0, abs_tol=1e-10):
                raise ValueError(f"The configured base-year sales index must be 100: {key}")
    if actual_keys != expected_keys:
        raise ValueError("Metric records do not cover exactly the configured analysis.")
    if len(metric_df) != config.get_observation_count() * len(config.metrics):
        raise ValueError("Metric row count does not match the configured study.")


def save_metric_results(database, config, metric_df, signature):
    """Replace this run atomically without mixing source versions."""
    columns_sql = ", ".join(METRIC_COLUMNS)
    placeholders = ", ".join(["?"] * len(METRIC_COLUMNS))
    with database.connection:
        current_sources = database.read_selected_records(config)
        if make_run_signature(config, current_sources) != signature:
            raise ValueError("Source records changed. Reload and recalculate before saving.")
        database.connection.execute(
            "DELETE FROM metric_results WHERE study_id = ? AND config_signature = ?",
            (config.study_id, signature),
        )
        for row in metric_df.to_dict("records"):
            values = []
            for column in METRIC_COLUMNS:
                value = row[column]
                if pd.isna(value):
                    value = None
                values.append(value)
            database.connection.execute(
                f"INSERT INTO metric_results ({columns_sql}) VALUES ({placeholders})",
                tuple(values),
            )
    return len(metric_df)


def read_metric_results(database, config, signature):
    """Query only the selected study and input signature."""
    query = """
        SELECT study_id, config_signature, unit_id, analysis_year, metric_name,
               metric_value, value_unit, calculation_time, missing_reason
        FROM metric_results
        WHERE study_id = ? AND config_signature = ?
        ORDER BY unit_id, analysis_year, metric_name
    """
    return pd.read_sql_query(query, database.connection, params=[config.study_id, signature])


def verify_metric_copy(metric_df, stored_metric_df):
    """Compare all persisted fields, treating missing values consistently."""
    keys = ["unit_id", "analysis_year", "metric_name"]
    left = metric_df.sort_values(keys).reset_index(drop=True).to_dict("records")
    right = stored_metric_df.sort_values(keys).reset_index(drop=True).to_dict("records")
    if len(left) != len(right):
        raise ValueError("Persisted metric count does not match.")
    for left_row, right_row in zip(left, right):
        for column in METRIC_COLUMNS:
            first = left_row[column]
            second = right_row[column]
            if pd.isna(first) and pd.isna(second):
                continue
            if pd.isna(first) or pd.isna(second):
                raise ValueError(f"Persisted missing status differs: {column}")
            if column == "metric_value":
                if not math.isclose(float(first), float(second), rel_tol=1e-12, abs_tol=1e-10):
                    raise ValueError("Persisted metric value differs.")
            elif first != second:
                raise ValueError(f"Persisted metric metadata differs: {column}")


def build_stage_summary(analysis_df, config):
    """Report unweighted means and the number of available annual values."""
    stages = []
    for period in config.periods:
        stage = period["comparison_stage"].strip()
        if stage not in stages:
            stages.append(stage)
    rows = []
    for unit in config.business_units:
        for stage in stages:
            selected = analysis_df[
                (analysis_df["unit_id"] == unit["unit_id"])
                & (analysis_df["comparison_stage"] == stage)
            ]
            years = []
            for year in selected["analysis_year"]:
                years.append(str(year))
            row = {
                "unit_id": unit["unit_id"],
                "company_name": unit["company_name"],
                "segment_name": unit["segment_name"],
                "comparison_stage": stage,
                "analysis_years": ", ".join(years),
                "record_count": len(selected),
            }
            for metric in config.metrics:
                column = METRIC_SPECS[metric]["column"]
                values = selected[column].dropna()
                row[column + "_valid_years"] = len(values)
                if len(values) == 0:
                    row[column + "_mean"] = None
                else:
                    row[column + "_mean"] = float(values.mean())
            rows.append(row)
    return pd.DataFrame(rows)
