import json
import logging
from pathlib import Path
from datetime import datetime
from ingestion.helpers import make_metadata


from core.load_settings import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_interior_styles():
    file_path = Path(settings["data"]["processed_dir"]) / "interiorStyles.json"

    if not file_path.exists():
        logger.error(f"File {file_path} does not exist.")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            interior_styles = json.load(f)
            logger.info(f"Loaded {len(interior_styles)} records from {file_path}.")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(interior_styles, dict):
        interior_styles = [interior_styles] # chuyển thành kiểu list nếu là dict  

    if not isinstance(interior_styles, list):
        logger.error(f"Data in {file_path} is not a list or dict.")
        return []

    if not interior_styles:
        logger.warning(f"No interior styles found in {file_path}.")
        return []

    chunks =[]

    for idx, interior_style in enumerate(interior_styles):
        if not isinstance(interior_style, dict):
            logger.warning(f"Record at index {idx} is not a dict. Skipping.")
            continue


        interior_style_id = interior_style.get("id")
        interior_style_name = interior_style.get("name","")
        interior_style_slug = interior_style.get("slug")
        interior_style_image = interior_style.get("image","")

        if not interior_style_name or not isinstance(interior_style_name, str):
            logger.warning(f"Record at index {idx} has no valid 'name'. Skipping.")
            continue

        if not interior_style_image or not isinstance(interior_style_image, str):
            logger.warning(f"Record at index {idx} has no valid 'image'. Skipping.")
            continue

        base_metadata = {
                    "type": "interior_style",
                    "source": "interiorStyles.json",
                    "interior_style_id": interior_style_id,
                    "interior_style_name": interior_style_name,
                    "interior_style_slug": interior_style_slug,
                    "interior_style_image": interior_style_image,
                    "created_at": datetime.utcnow().isoformat(),
                    "language":"vi"

                }
        
        text_parts = [
            f"Loại nội thất: {interior_style_name}"
            f"Hình ảnh minh họa nội thất {interior_style_name} : {interior_style_image}"
        ]

        chunks.append({
                "text": "\n".join(text_parts),
                "metadata":make_metadata(base_metadata,chunk_type="definition",priority=3)  
        })
    if not chunks:
        logger.warning(f"No valid chunks created from {file_path}.")

    return chunks



