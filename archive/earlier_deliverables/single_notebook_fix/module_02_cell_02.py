# Cell 02: Load Study Configuration and Set Input Paths

CONFIG_PATH = Path.cwd() / "study.json"

config = load_study_config(CONFIG_PATH)
paths = config.resolve_paths(CONFIG_PATH)
DATA_FILE = paths["data_file"]
DATABASE_FILE = paths["database_file"]
RAW_DIRECTORY = DATA_FILE.parent / "raw"
CLEAN_FILE = DATA_FILE.parent / "clean" / "financial_records.csv"

RAW_FILES = {
    "amazon_north_america": RAW_DIRECTORY / "amazon_segment_raw.csv",
    "walmart_us": RAW_DIRECTORY / "walmart_segment_raw.csv",
}

print(f"Working directory: {Path.cwd()}")
print(f"Configuration: {CONFIG_PATH}")
print(f"Planned records: {config.get_observation_count()}")
print(f"Index base year: {config.index_base_year}")
print(f"Database: {DATABASE_FILE}")