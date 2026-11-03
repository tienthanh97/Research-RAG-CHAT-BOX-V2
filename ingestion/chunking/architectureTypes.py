import json
import logging
from pathlib import Path
from datetime import datetime
from ingestion.helpers import make_metadata


from core.load_settings import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")

def chunk_architecture_types():
    file_path = Path(settings["data"]["processed_dir"]) / "architectureTypes.json"

    if not file_path.exists():
        logger.error(f"File {file_path} does not exist.")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            architecture_types = json.load(f)
            logger.info(f"Loaded {len(architecture_types)} records from {file_path}.")
    except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format {e}")
            return []
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(architecture_types, dict):
        architecture_types = [architecture_types] # chuyển thành kiểu list nếu là dict  

    if not isinstance(architecture_types, list):
        logger.error(f"Data in {file_path} is not a list or dict.")
        return []

    if not architecture_types:
        logger.warning(f"No architecture types found in {file_path}.")
        return []

    chunks =[]

    for idx, architecture_type in enumerate(architecture_types):
        if not isinstance(architecture_type, dict):
            logger.warning(f"Record at index {idx} is not a dict. Skipping.")
            continue


        architecture_id = architecture_type.get("id")
        architecture_name = architecture_type.get("name","")
        architecture_slug = architecture_type.get("slug")
        architecture_image = architecture_type.get("image","")

        if not architecture_name :
            logger.warning(f"Record at index {idx} has no valid 'name'. Skipping.")
            continue

        if not architecture_image :
            logger.warning(f"Record at index {idx} has no valid 'image'. Skipping.")
            continue

        base_metadata = {
                    "type": "architecture_type",
                    "source": "architectureTypes.json",
                    "architecture_id": architecture_id,
                    "architecture_name": architecture_name,
                    "architecture_slug": architecture_slug,
                    "architecture_image": architecture_image

                }

        text_parts = [
            f"Loại kiến trúc: {architecture_name}"
            f"Hình ảnh minh họa kiến trúc {architecture_name} : {architecture_image}"
        ]

        chunks.append({
                "text": "\n".join(text_parts),
                "metadata": make_metadata(base_metadata,chunk_type = "definition",priority =3)
        })
        
    if not chunks:
        logger.warning(f"No valid chunks created from {file_path}.")

    return chunks



