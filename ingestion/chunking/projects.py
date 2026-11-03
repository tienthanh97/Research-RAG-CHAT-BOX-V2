import json
import logging
from pathlib import Path
from ingestion.helpers import make_metadata
from datetime import datetime

from core.load_settings import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")




def chunk_projects():
    file_path = Path(settings["data"]["processed_dir"]) / "projects.json"

    if not file_path.exists():
        logger.error(f"File {file_path} does not exist.")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            projects = json.load(f)
            logger.info(f"Loaded {len(projects)} records from {file_path}.")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(projects, dict):
        projects = [projects] # chuyển thành kiểu list nếu là dict  

    if not isinstance(projects, list):
        logger.error(f"Data in {file_path} is not a list or dict.")
        return []

    if not projects:
        logger.warning(f"No projects found in {file_path}.")
        return []

    chunks =[]

    for idx, project in enumerate(projects):
        if not isinstance(project, dict):
            logger.warning(f"Record at index {idx} is not a dict. Skipping.")
            continue


        project_id = project.get("id")
        project_title= project.get("title","")
        project_slug = project.get("slug")
        project_description = project.get("description","")
        project_investor = project.get("investor")
        project_location = project.get("location")
        project_area = project.get("area")
        project_complete_date = project.get("complete_date")

        project_category = project.get("category", {})

        project_interior_style = project.get("interior_style", {})

        project_architecture_type = project.get("architectureType", {})
     
        base_metadata = {
            "type":"project",
            "source":"project.json",
            "project_id":project_id,
            "project_title":project_title,
            "project_slug":project_slug,
            "create_at":datetime.utcnow().isoformat(),
            "language":"vi",
        }

        CHUNK_PRIORITY = {
            "overview_title": 1,
            "overview_description": 2,
             "overview_architecture_interior": 3,
            "overview_location_investor": 4,
            "overview_specs": 5
           
        }

        # Chunk overview
        if project_title:
            chunks.append({
                "text": f"Tiêu đề dự án: {project_title}",
                "metadata": make_metadata(base_metadata, chunk_type="overview_title",priority = CHUNK_PRIORITY.overview_title)
            })

        # Chunk description
        if project_description:
            chunks.append({
                "text": f"Mô tả dự án: {project_description}",
                "metadata": make_metadata(base_metadata, chunk_type="overview_description",priority = CHUNK_PRIORITY.overview_description)
            })

        # Chunk Location + Investor
        if project_location or project_investor:
            text_parts = []
            if project_location:
                text_parts.append(f"Vị trí: {project_location}")
            if project_investor:
                text_parts.append(f"Chủ đầu tư: {project_investor}")
            chunks.append({
                "text": " | ".join(text_parts),
                "metadata": make_metadata(base_metadata, chunk_type="overview_location_investor",priority = CHUNK_PRIORITY.overview_location_investor)
            })

        # Chunk Specs
        if project_area or project_complete_date:
            text_parts = []
            if project_area:
                text_parts.append(f"Diện tích: {project_area}")
            if project_complete_date:
                text_parts.append(f"Ngày hoàn thành: {project_complete_date}")
            chunks.append({
                "text": " | ".join(text_parts),
                "metadata": make_metadata(base_metadata, chunk_type="overview_specs",priority = CHUNK_PRIORITY.overview_specs)
            })

        # Chunk kien truc va noi that
        if project_architecture_type or project_interior_style:
            text_parts = []
            if project_architecture_type:
                arch_type_name = project_architecture_type.get("name", "")
                if arch_type_name:
                    text_parts.append(f"Loại kiến trúc: {arch_type_name}")
            if project_interior_style:
                interior_style_name = project_interior_style.get("name", "")
                if interior_style_name:
                    text_parts.append(f"Phong cách nội thất: {interior_style_name}")
            chunks.append({
                "text": " | ".join(text_parts),
                "metadata": make_metadata(base_metadata, chunk_type="overview_architecture_interior", priority=CHUNK_PRIORITY["overview_architecture_interior"])
            })


    

    return chunks



