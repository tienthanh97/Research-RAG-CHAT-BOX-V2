import json
import logging
from pathlib import Path
from datetime import datetime
from ingestion.helpers import make_metadata

from core.load_settings import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_project_categories():
    file_path = Path(settings["data"]["processed_dir"]) / "projectCategories.json"

    if not file_path.exists():
        logger.error(f"File {file_path} does not exist.")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            project_categories = json.load(f)
            logger.info(f"Loaded {len(project_categories)} records from {file_path}.")
    except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format {e}")
            return []
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(project_categories, dict):
        project_categories = [project_categories] # chuyển thành kiểu list nếu là dict  

    if not isinstance(project_categories, list):
        logger.error(f"Data in {file_path} is not a list or dict.")
        return []

    if not project_categories:
        logger.warning(f"No project categories found in {file_path}.")
        return []

    chunks =[]

    for idx, project_category in enumerate(project_categories):
        if not isinstance(project_category, dict):
            logger.warning(f"Record at index {idx} is not a dict. Skipping.")
            continue


        category_id = project_category.get("id")
        category_name = project_category.get("name","")
        category_slug = project_category.get("slug")

        if not category_name:
            logger.warning(f"Skipping project category with invalid name at index {idx}")
            continue

        base_metadata ={
                "type": "project_category",
                "source": "ProjectCategories.json",
                "category_id": category_id,
                "category_name": category_name,
                "category_slug": category_slug,
                "created_at": datetime.utcnow().isoformat(),
                "language": "vi"
            }

        text_parts = [
            f"Tên loại dự án: {category_name}",
            f"Loại dự án này được dùng để phân loại các dự án liên quan đến {category_name}."
        ]

        chunks.append({
            "text": "\n".join(text_parts),
            "metadata": make_metadata(base_metadata,chunk_type = "definition",priority = 3)
        })


    return chunks



