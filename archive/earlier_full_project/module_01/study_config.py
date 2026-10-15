"""Manage study settings with simple classes and ordinary functions."""

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse


SUPPORTED_METRICS = ["sales_growth", "operating_margin", "sales_index"]


def check_text(value, field_name):
    """Check that a setting contains non-empty text."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")


def check_year(value, field_name):
    """Check that a setting contains a reasonable integer year."""
    if type(value) is not int:
        raise ValueError(f"{field_name} must be an integer.")
    if value < 1900 or value > 2100:
        raise ValueError(f"{field_name} must be between 1900 and 2100.")


class StudyConfig:
    """Store and validate one study without collecting financial data."""

    def __init__(self, settings):
        if not isinstance(settings, dict):
            raise ValueError("Study settings must be a dictionary.")

        required_fields = [
            "study_id", "title", "research_question", "frequency", "currency",
            "business_units", "periods", "metrics", "index_base_year",
            "missing_previous_period", "alignment_note", "data_file",
            "results_directory",
        ]
        for field_name in required_fields:
            if field_name not in settings:
                raise ValueError(f"Missing study setting: {field_name}")

        self.study_id = settings["study_id"]
        self.title = settings["title"]
        self.research_question = settings["research_question"]
        self.frequency = settings["frequency"]
        self.currency = settings["currency"]
        self.business_units = settings["business_units"]
        self.periods = settings["periods"]
        self.metrics = settings["metrics"]
        self.index_base_year = settings["index_base_year"]
        self.missing_previous_period = settings["missing_previous_period"]
        self.alignment_note = settings["alignment_note"]
        self.data_file = settings["data_file"]
        self.results_directory = settings["results_directory"]
        self.database_file = settings.get("database_file", "../data/retail_comparison.sqlite")
        self.validate()

    def validate(self):
        """Check content before later modules use the configuration."""
        values = self.to_dict()
        text_fields = [
            "study_id", "title", "research_question", "currency",
            "alignment_note", "data_file", "results_directory", "database_file",
        ]
        for field_name in text_fields:
            check_text(values[field_name], field_name)

        if self.frequency != "annual":
            raise ValueError("Only annual studies are supported.")
        if len(self.currency) != 3 or not self.currency.isalpha() or not self.currency.isupper():
            raise ValueError("Currency must be a three-letter uppercase code.")
        if not isinstance(self.business_units, list) or len(self.business_units) < 2:
            raise ValueError("A comparison requires at least two business units.")

        unit_ids = []
        for unit in self.business_units:
            if not isinstance(unit, dict):
                raise ValueError("Each business unit must be a dictionary.")
            for field_name in ["unit_id", "company_name", "ticker", "segment_name", "currency"]:
                check_text(unit.get(field_name), field_name)
            if unit["unit_id"] in unit_ids:
                raise ValueError("Business unit IDs must be unique.")
            unit_ids.append(unit["unit_id"])
            if unit["currency"] != self.currency:
                raise ValueError("All business units must use the study currency.")

            sources = unit.get("source_urls")
            if not isinstance(sources, list) or len(sources) == 0:
                raise ValueError("Each business unit needs a list of source URLs.")
            for url in sources:
                check_text(url, "source_url")
                parsed_url = urlparse(url)
                if parsed_url.scheme not in ["http", "https"] or not parsed_url.netloc:
                    raise ValueError(f"Invalid source URL: {url}")

            notes = unit.get("scope_notes")
            if not isinstance(notes, list) or len(notes) == 0:
                raise ValueError("Each business unit needs a list of scope notes.")
            for note in notes:
                check_text(note, "scope_note")

        if not isinstance(self.periods, list) or len(self.periods) < 2:
            raise ValueError("A trend comparison requires at least two annual periods.")

        analysis_years = []
        previous_fiscal_years = {}
        for period in self.periods:
            if not isinstance(period, dict):
                raise ValueError("Each period must be a dictionary.")
            year = period.get("analysis_year")
            check_year(year, "analysis_year")
            if len(analysis_years) > 0 and year != analysis_years[-1] + 1:
                raise ValueError("Analysis years must be consecutive and ordered.")
            analysis_years.append(year)

            fiscal_years = period.get("fiscal_years")
            if not isinstance(fiscal_years, dict):
                raise ValueError("Fiscal years must be a dictionary.")
            if set(fiscal_years.keys()) != set(unit_ids):
                raise ValueError("Each period must map exactly the configured business units.")
            for unit_id in unit_ids:
                fiscal_year = fiscal_years[unit_id]
                check_year(fiscal_year, "fiscal_year")
                if unit_id in previous_fiscal_years:
                    if fiscal_year != previous_fiscal_years[unit_id] + 1:
                        raise ValueError("Each unit's fiscal years must be consecutive and ordered.")
                previous_fiscal_years[unit_id] = fiscal_year

        if not isinstance(self.metrics, list) or len(self.metrics) == 0:
            raise ValueError("Metrics must be a non-empty list.")
        used_metrics = []
        for metric in self.metrics:
            if metric not in SUPPORTED_METRICS:
                raise ValueError("Supported metrics: sales_growth, operating_margin, sales_index.")
            if metric in used_metrics:
                raise ValueError("Metric IDs must be unique.")
            used_metrics.append(metric)

        check_year(self.index_base_year, "index_base_year")
        if self.index_base_year not in analysis_years:
            raise ValueError("The index base year must be an analysis year.")
        if self.missing_previous_period != "leave_missing":
            raise ValueError("Missing growth must be left missing, not replaced with zero.")

        for file_path in [self.data_file, self.database_file, self.results_directory]:
            if Path(file_path).is_absolute():
                raise ValueError("Data, database, and result paths must be relative to the configuration file.")
        if Path(self.database_file).suffix.lower() not in [".sqlite", ".sqlite3", ".db"]:
            raise ValueError("Database files must use .sqlite, .sqlite3, or .db.")
        if Path(self.data_file) == Path(self.database_file):
            raise ValueError("The import file and database must have different paths.")

    def get_observation_count(self):
        """Return the planned number of segment-year observations."""
        return len(self.business_units) * len(self.periods)

    def resolve_paths(self, config_path):
        """Resolve paths without creating files or a database."""
        base_folder = Path(config_path).resolve().parent
        return {
            "data_file": (base_folder / self.data_file).resolve(),
            "database_file": (base_folder / self.database_file).resolve(),
            "results_directory": (base_folder / self.results_directory).resolve(),
        }

    def to_dict(self):
        """Prepare configuration content for JSON storage."""
        return {
            "study_id": self.study_id,
            "title": self.title,
            "research_question": self.research_question,
            "frequency": self.frequency,
            "currency": self.currency,
            "business_units": self.business_units,
            "periods": self.periods,
            "metrics": self.metrics,
            "index_base_year": self.index_base_year,
            "missing_previous_period": self.missing_previous_period,
            "alignment_note": self.alignment_note,
            "data_file": self.data_file,
            "results_directory": self.results_directory,
            "database_file": self.database_file,
        }


def save_study_config(config, file_path):
    """Save settings only; do not create a financial database."""
    config.validate()
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(config.to_dict(), file, indent=2, ensure_ascii=True)
        file.write("\n")


def load_study_config(file_path):
    """Load a JSON file and construct a validated study object."""
    with open(file_path, "r", encoding="utf-8") as file:
        settings = json.load(file)
    return StudyConfig(settings)


def main():
    parser = argparse.ArgumentParser(description="Validate a retail comparison study configuration.")
    parser.add_argument("--config", default=Path(__file__).with_name("study.json"))
    args = parser.parse_args()
    try:
        config = load_study_config(args.config)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print("Configuration is valid.")
    print(f"Study: {config.title}")
    print(f"Planned observations: {config.get_observation_count()}")
    print("Financial data has not been loaded or calculated.")


if __name__ == "__main__":
    main()
