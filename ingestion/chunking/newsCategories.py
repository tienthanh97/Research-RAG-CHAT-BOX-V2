import json
import logging
from pathlib import Path
from datetime import datetime 
from ingestion.helpers import make_metadata

from core.load_settings import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_news_categories():
    file_path = Path(settings["data"]["processed_dir"]) / "newsCategories.json"

    if not file_path.exists():
        logger.error(f"File {file_path} does not exist.")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            news_categories = json.load(f)
            logger.info(f"Loaded {len(news_categories)} records from {file_path}.")
    except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format {e}")
            return []
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(news_categories, dict):
        news_categories = [news_categories] # chuyển thành kiểu list nếu là dict  

    if not isinstance(news_categories, list):
        logger.error(f"Data in {file_path} is not a list or dict.")
        return []

    if not news_categories:
        logger.warning(f"No news categories found in {file_path}.")
        return []

    chunks =[]

    for idx, news_category in enumerate(news_categories):
        if not isinstance(news_category, dict):
            logger.warning(f"Record at index {idx} is not a dict. Skipping.")
            continue


        category_id = news_category.get("id")
        category_name = news_category.get("name","")
        category_slug = news_category.get("slug")

        if not category_name:
            logger.warning(f"Skipping news category with missing name at index {idx}")
            continue

        base_metadata={
                    "type": "news_category",
                    "category_id": category_id,
                    "category_name": category_name,
                    "category_slug": category_slug,
                    "source": "newsCategories.json",
                    "created_at": datetime.utcnow().isoformat(),
                    "language": "vi"
            }
        
        text_parts = [
            f"Tên danh mục tin tức: {category_name}",
            f"Danh mục này được dùng để phân loại các bài viết liên quan đến {category_name}."
        ]
        chunks.append({
            "text": "\n".join(text_parts),
            "metadata": make_metadata(base_metadata,chunk_type = "definition",priority =3)
        })


    return chunks



