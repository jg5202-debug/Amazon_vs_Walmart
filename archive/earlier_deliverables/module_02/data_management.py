"""Clean annual segment records and store them in a local SQLite database."""

import math
import re
import sqlite3
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd


RAW_COLUMNS = [
    "unit_id", "company_name", "segment_name", "fiscal_year",
    "period_start", "period_end", "net_sales_raw", "operating_income_raw",
    "reported_currency", "reported_unit", "source_url", "source_section",
    "accessed_date", "date_basis",
]

UNIT_MULTIPLIERS = {"units": 0.000001, "millions": 1.0, "billions": 1000.0}

RECORD_COLUMNS = [
    "unit_id", "fiscal_year", "period_start", "period_end",
    "net_sales_raw", "operating_income_raw", "reported_currency",
    "reported_unit", "source_url", "source_section", "accessed_date",
    "date_basis", "net_sales_usd_m", "operating_income_usd_m",
]


def parse_amount(value):
    """Convert a reported amount string without treating missing data as zero."""
    text = str(value).strip().replace(",", "")
    if text.startswith("(") and text.endswith(")"):
        text = "-" + text[1:-1]
    if re.fullmatch(r"-?\d+(\.\d+)?", text) is None:
        raise ValueError(f"Invalid reported amount: {value}")
    amount = float(pd.to_numeric(text, errors="raise"))
    if not math.isfinite(amount):
        raise ValueError(f"Reported amount must be finite: {value}")
    return amount


def standardize_records(raw_df):
    """Preserve source strings and add numeric amounts in USD millions."""
    for column in RAW_COLUMNS:
        if column not in raw_df.columns:
            raise ValueError(f"Missing raw column: {column}")

    clean_df = raw_df[RAW_COLUMNS].copy()
    for column in RAW_COLUMNS:
        if clean_df[column].isna().any():
            raise ValueError(f"Missing value in column: {column}")
        clean_df[column] = clean_df[column].astype(str).str.strip()
        if clean_df[column].eq("").any():
            raise ValueError(f"Blank value in column: {column}")

    years = pd.to_numeric(clean_df["fiscal_year"], errors="raise")
    if not years.between(1900, 2100).all() or not years.eq(years.round()).all():
        raise ValueError("Fiscal years must be integer years between 1900 and 2100.")
    clean_df["fiscal_year"] = years.astype(int)

    for column in ["period_start", "period_end", "accessed_date"]:
        dates = pd.to_datetime(clean_df[column], format="%Y-%m-%d", errors="raise")
        clean_df[column] = dates.dt.strftime("%Y-%m-%d")

    sales_values = []
    income_values = []
    for row in clean_df.to_dict("records"):
        if row["reported_currency"] != "USD":
            raise ValueError("This version supports USD records only; it does not convert currencies.")
        if row["reported_unit"] not in UNIT_MULTIPLIERS:
            raise ValueError(f"Unsupported reported unit: {row['reported_unit']}")
        multiplier = UNIT_MULTIPLIERS[row["reported_unit"]]
        sales_values.append(parse_amount(row["net_sales_raw"]) * multiplier)
        income_values.append(parse_amount(row["operating_income_raw"]) * multiplier)

    clean_df["net_sales_usd_m"] = sales_values
    clean_df["operating_income_usd_m"] = income_values
    return clean_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)


def validate_records(clean_df, config):
    """Require exact configured coverage, correct identities and usable values."""
    if config.currency != "USD":
        raise ValueError("The configuration must use USD for this version.")
    if clean_df.duplicated(["unit_id", "fiscal_year"]).any():
        raise ValueError("Duplicate segment/fiscal-year records were found.")

    expected_keys = set()
    units_by_id = {}
    for unit in config.business_units:
        units_by_id[unit["unit_id"]] = unit
    for period in config.periods:
        for unit_id in units_by_id:
            expected_keys.add((unit_id, period["fiscal_years"][unit_id]))

    actual_keys = set()
    for row in clean_df.to_dict("records"):
        key = (row["unit_id"], row["fiscal_year"])
        actual_keys.add(key)
        if row["unit_id"] not in units_by_id:
            raise ValueError(f"Unexpected business unit: {row['unit_id']}")
        unit = units_by_id[row["unit_id"]]
        if row["company_name"] != unit["company_name"] or row["segment_name"] != unit["segment_name"]:
            raise ValueError(f"Company or segment name does not match configuration: {key}")
        if row["reported_currency"] != config.currency:
            raise ValueError(f"Currency does not match configuration: {key}")
        if row["period_start"] >= row["period_end"]:
            raise ValueError(f"Report start must be before report end: {key}")
        for column in ["net_sales_usd_m", "operating_income_usd_m"]:
            if not math.isfinite(float(row[column])):
                raise ValueError(f"Non-finite financial value in {column}: {key}")
        if row["net_sales_usd_m"] <= 0:
            raise ValueError(f"Net sales must be positive: {key}")
        source = urlparse(row["source_url"])
        if source.scheme not in ["http", "https"] or not source.netloc:
            raise ValueError(f"Invalid source URL: {key}")
        for column in ["source_section", "date_basis", "accessed_date"]:
            if not str(row[column]).strip():
                raise ValueError(f"Missing provenance in {column}: {key}")

    if actual_keys != expected_keys:
        missing = sorted(expected_keys - actual_keys)
        extra = sorted(actual_keys - expected_keys)
        raise ValueError(f"Coverage mismatch. Missing: {missing}; extra: {extra}")
    if len(clean_df) != config.get_observation_count():
        raise ValueError("Record count does not match the configured study.")


class DatabaseManager:
    """Own the database connection without embedding company-specific rules."""

    def __init__(self, database_path):
        self.database_path = Path(database_path)
        self.connection = None

    def connect(self):
        if self.connection is None:
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            self.connection = sqlite3.connect(str(self.database_path))
            self.connection.execute("PRAGMA foreign_keys = ON")

    def create_tables(self):
        self.connection.executescript("""
            CREATE TABLE IF NOT EXISTS business_units (
                unit_id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                ticker TEXT NOT NULL,
                segment_name TEXT NOT NULL,
                currency TEXT NOT NULL,
                scope_notes TEXT NOT NULL,
                source_urls TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS financial_records (
                unit_id TEXT NOT NULL,
                fiscal_year INTEGER NOT NULL,
                period_start TEXT NOT NULL,
                period_end TEXT NOT NULL,
                net_sales_raw TEXT NOT NULL,
                operating_income_raw TEXT NOT NULL,
                reported_currency TEXT NOT NULL CHECK (reported_currency = 'USD'),
                reported_unit TEXT NOT NULL,
                source_url TEXT NOT NULL,
                source_section TEXT NOT NULL,
                accessed_date TEXT NOT NULL,
                date_basis TEXT NOT NULL,
                net_sales_usd_m REAL NOT NULL CHECK (net_sales_usd_m > 0),
                operating_income_usd_m REAL NOT NULL,
                PRIMARY KEY (unit_id, fiscal_year),
                FOREIGN KEY (unit_id) REFERENCES business_units(unit_id),
                CHECK (period_start < period_end)
            );
            CREATE TABLE IF NOT EXISTS metric_results (
                study_id TEXT NOT NULL,
                config_signature TEXT NOT NULL,
                unit_id TEXT NOT NULL,
                analysis_year INTEGER NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL,
                value_unit TEXT NOT NULL,
                calculation_time TEXT NOT NULL,
                missing_reason TEXT,
                PRIMARY KEY (study_id, config_signature, unit_id, analysis_year, metric_name),
                FOREIGN KEY (unit_id) REFERENCES business_units(unit_id)
            );
        """)

    def save_data(self, config, clean_df):
        counts = {"inserted": 0, "updated": 0, "unchanged": 0}
        columns_sql = ", ".join(RECORD_COLUMNS)
        placeholders = ", ".join(["?"] * len(RECORD_COLUMNS))
        update_parts = []
        for column in RECORD_COLUMNS[2:]:
            update_parts.append(column + " = ?")
        update_sql = ", ".join(update_parts)

        with self.connection:
            for unit in config.business_units:
                unit_values = (
                    unit["company_name"], unit["ticker"], unit["segment_name"],
                    unit["currency"], "\n".join(unit["scope_notes"]),
                    "\n".join(unit["source_urls"]),
                )
                existing_unit = self.connection.execute(
                    "SELECT company_name, ticker, segment_name, currency, scope_notes, source_urls "
                    "FROM business_units WHERE unit_id = ?", (unit["unit_id"],)
                ).fetchone()
                if existing_unit is None:
                    self.connection.execute(
                        "INSERT INTO business_units "
                        "(company_name, ticker, segment_name, currency, scope_notes, source_urls, unit_id) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?)", unit_values + (unit["unit_id"],)
                    )
                elif existing_unit != unit_values:
                    self.connection.execute(
                        "UPDATE business_units SET company_name = ?, ticker = ?, segment_name = ?, "
                        "currency = ?, scope_notes = ?, source_urls = ? WHERE unit_id = ?",
                        unit_values + (unit["unit_id"],)
                    )
                    self.connection.execute("DELETE FROM metric_results WHERE unit_id = ?", (unit["unit_id"],))

            for row in clean_df.to_dict("records"):
                values = []
                for column in RECORD_COLUMNS:
                    values.append(row[column])
                values = tuple(values)
                key = (row["unit_id"], row["fiscal_year"])
                existing = self.connection.execute(
                    f"SELECT {columns_sql} FROM financial_records WHERE unit_id = ? AND fiscal_year = ?", key
                ).fetchone()
                if existing is None:
                    self.connection.execute(
                        f"INSERT INTO financial_records ({columns_sql}) VALUES ({placeholders})", values
                    )
                    counts["inserted"] += 1
                    self.connection.execute("DELETE FROM metric_results WHERE unit_id = ?", (row["unit_id"],))
                elif existing != values:
                    self.connection.execute(
                        f"UPDATE financial_records SET {update_sql} WHERE unit_id = ? AND fiscal_year = ?",
                        values[2:] + key,
                    )
                    counts["updated"] += 1
                    self.connection.execute("DELETE FROM metric_results WHERE unit_id = ?", (row["unit_id"],))
                else:
                    counts["unchanged"] += 1
        return counts

    def read_selected_records(self, config):
        frames = []
        for unit in config.business_units:
            years = []
            for period in config.periods:
                years.append(period["fiscal_years"][unit["unit_id"]])
            placeholders = ", ".join(["?"] * len(years))
            parameters = [unit["unit_id"]] + years
            query = f"""
                SELECT f.*, b.company_name, b.segment_name
                FROM financial_records AS f
                JOIN business_units AS b ON f.unit_id = b.unit_id
                WHERE f.unit_id = ? AND f.fiscal_year IN ({placeholders})
                ORDER BY f.fiscal_year
            """
            frames.append(pd.read_sql_query(query, self.connection, params=parameters))
        financial_df = pd.concat(frames, ignore_index=True)
        return financial_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)

    def get_table_counts(self):
        counts = {}
        for table in ["business_units", "financial_records", "metric_results"]:
            row = self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
            counts[table] = row[0]
        return counts

    def close(self):
        if self.connection is not None:
            self.connection.close()
            self.connection = None


def verify_database_copy(clean_df, financial_df):
    """Compare every imported field after reading the persisted records back."""
    left = clean_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)
    right = financial_df.sort_values(["unit_id", "fiscal_year"]).reset_index(drop=True)
    if len(left) != len(right):
        raise ValueError("Database row count does not match the accepted records.")
    for column in left.columns:
        if column not in right.columns or left[column].tolist() != right[column].tolist():
            raise ValueError(f"Database values differ from accepted records: {column}")
