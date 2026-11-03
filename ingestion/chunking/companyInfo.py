import json
import logging
from pathlib import Path
from datetime import datetime
from ingestion.helpers import make_metadata

from core.load_settings import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")


def chunk_company_info():
    file_path = Path(settings["data"]["processed_dir"]) / "companyInfo.json"

    if not file_path.exists():
        logger.error(f"File {file_path} does not exist.")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            company_info = json.load(f)
            logger.info(
                f"Loaded {len(company_info)} records from {file_path}.")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON format {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(company_info, dict):
        company_info = [company_info]  # chuyển thành kiểu list nếu là dict

    if not isinstance(company_info, list):
        logger.error(f"Data in {file_path} is not a list or dict.")
        return []

    if not company_info:
        logger.warning(f"No company info found in {file_path}.")
        return []

    chunks = []

    for idx, company in enumerate(company_info):
        if not isinstance(company, dict):
            logger.warning(f"Record at index {idx} is not a dict. Skipping.")
            continue

        company_name = company.get("companyName", "")
        company_slogan = company.get("companySlogan", "")
        company_description = company.get("companyDescription", "")
        company_hotlines = company.get("hotlines", [])
        company_emails = company.get("emails", [])
        company_main_address = company.get("mainAddress", "")
        company_working_hours = company.get("workingHours", "")
        company_website = company.get("website", "")
        company_social_links = company.get("socialLinks", {})
        company_total_employees = company.get("totalEmployees")
        company_total_projects = company.get("totalProjects")

        # if not company_name :
        #     logger.warning(f"Record at index {idx} has no valid 'companyName'. Skipping.")
        #     continue
        # if not company_slogan :
        #     logger.warning(f"Record at index {idx} has no valid 'companySlogan'. Skipping.")
        #     continue
        # if not company_description or not isinstance(company_description, str):
        #     logger.warning(f"Record at index {idx} has no valid 'companyDescription'. Skipping.")
        #     continue
        # if  not isinstance(company_working_hours, str):
        #     logger.warning(f"Record at index {idx} has no valid 'companyWorkingHours'. Skipping.")
        #     continue
        # if not company_website or not isinstance(company_website, str):
        #     logger.warning(f"Record at index {idx} has no valid 'companyWebsite'. Skipping.")
        #     continue

        # if not company_main_address or not isinstance(company_main_address, str):
        #     logger.warning(f"Record at index {idx} has no valid 'companyMainAddress'. Skipping.")
        #     continue

        # if not isinstance(company_hotlines, list):
        #     logger.warning(f"Record at index {idx} has no valid 'companyHotlines'. Skipping.")
        #     continue
        # if not isinstance(company_emails, list):
        #     logger.warning(f"Record at index {idx} has no valid 'companyEmails'. Skipping.")
        #     continue
        # if not company_total_employees or not isinstance(company_total_employees, int):
        #     logger.warning(f"Record at index {idx} has no valid 'companyTotalEmployees'. Skipping.")
        #     continue

        # if not company_total_projects or not isinstance(company_total_projects, int):
        #     logger.warning(f"Record at index {idx} has no valid 'companyTotalProjects'. Skipping.")
        #     continue

        # kiem tra kieu du lieu co phai la dict khong. Vi du: { "facebook": "fb.com/xyz", "instagram": "insta.com/xyz" }
        if isinstance(company_social_links, dict):
            # chuyen doi dict thanh chuoi. Vi du: "facebook: fb.com/xyz, instagram: insta.com/xyz". Neu gia tri rong thi khong them vao chuoi
            company_social_text = ", ".join(
                [f"{key}: {value}" for key, value in company_social_links.items() if value])

        base_metadata = {
            "type": "company_info",
            "source": "companyInfo.json",
            "company_name": company_name,
            "created_at": datetime.utcnow().isoformat(),
            "language": "vi"
        }

        CHUNK_PRIORITY = {
            "overview": 1,
            "contact_details": 2,
            "social_link": 3,
            "additional_info": 4
        }

        # Chunk overview
        if company_name and company_slogan and company_description:
            chunks.append({
                "text": f"Tên công ty: {company_name}\nKhẩu hiệu: {company_slogan}\nMô tả: {company_description}",
                "metadata": make_metadata(base_metadata, chunk_type="overview", priority=CHUNK_PRIORITY["overview"])
            })

        # Chunk contact details
        if company_hotlines or company_emails or company_main_address or company_working_hours:
            text_parts = []
            if company_hotlines:
                text_parts.append(
                    f"Số điện thoại liên hệ: {', '.join(company_hotlines)}")
            if company_emails:
                text_parts.append(
                    f"Email liên hệ: {', '.join(company_emails)}")
            if company_main_address:
                text_parts.append(f"Địa chỉ chính: {company_main_address}")
            if company_working_hours:
                text_parts.append(f"Giờ làm việc: {company_working_hours}")

            chunks.append({
                "text": "\n".join(text_parts),
                "metadata": make_metadata(base_metadata, chunk_type="contact_details", priority=CHUNK_PRIORITY["contact_details"])
            })

        # Chunk social links
        if company_social_links or company_website:
            text_parts = []
            if company_website:
                text_parts.append(f"Website: {company_website}")
            if company_social_links:
                text_parts.append(f"Mạng xã hội: {company_social_links}")

            chunks.append({
                "text": "\n".join(text_parts),
                "metadata": make_metadata(base_metadata, chunk_type="social_links", priority=CHUNK_PRIORITY["social_links"])
            })

        # Chunk additional info
        if company_total_employees or company_total_projects:
            text_parts = []
            if company_total_employees:
                text_parts.append(
                    f"Tổng số nhân viên: {company_total_employees}")
            if company_total_projects:
                text_parts.append(
                    f"Tổng số dự án đã hoàn thành: {company_total_projects}")

            chunks.append({
                "text": "\n".join(text_parts),
                "metadata": make_metadata(base_metadata, chunk_type="additional_info", priority=CHUNK_PRIORITY["additional_info"])
            })

    return chunks
