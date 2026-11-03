import json
import logging
from pathlib import Path

from core.load_settings import load_settings
from core.setup_logging import setup_logging

setup_logging()
settings = load_settings()
logger = logging.getLogger("ingestion")

INPUT_PATH = Path(settings["data"]["raw_dir"]) 

OUTPUT_PATH = Path(settings["data"]["processed_dir"])

def load_data():
    """
    Load data from the raw directory and save it to the processed directory.
    """
    file_path = INPUT_PATH / "database_export_2026-01-23T02-02-46.json"

    if not file_path.exists():
        logger.error(f"File {file_path} does not exist.")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} records from {file_path}.")

    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    tables = data.get("tables", [])

    for table_name ,table_data in tables.items():
        if not table_data:
            logger.warning(f"No data found for table {table_name}. Skipping.")
            continue
        output_file = OUTPUT_PATH / f"{table_name}.json"
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(table_data, f, ensure_ascii=False, indent=4) # indent 4 for better readability (tab size = 4 spaces)
                logger.info(f"Saved {len(table_data)} records to {output_file}.")
        except Exception as e:
            logger.error(f"Error saving data to {output_file}: {e}")

if __name__ == "__main__":
    load_data() 