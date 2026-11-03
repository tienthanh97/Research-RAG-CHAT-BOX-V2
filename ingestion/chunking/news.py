import json
import logging
from pathlib import Path
from bs4 import BeautifulSoup

from ingestion.helpers import split_paragraphs
from ingestion.helpers import make_metadata

from datetime import datetime


from core.load_settings import load_settings

settings = load_settings()
logger = logging.getLogger("ingestion")

def html_to_text(html_content):
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator=" ", strip=True) # lây text từ html, loại bỏ thẻ html và khoảng trắng thừa
    

def chunk_news():
    file_path = Path(settings["data"]["processed_dir"]) / "news.json"

    if not file_path.exists():
        logger.error(f"File {file_path} does not exist.")
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            news = json.load(f)
            logger.info(f"Loaded {len(news)} records from {file_path}.")
    except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format {e}")
            return []
    except Exception as e:
        logger.error(f"Error loading data from {file_path}: {e}")
        return []

    if isinstance(news, dict):
        news = [news] # chuyển thành kiểu list nếu là dict  

    if not isinstance(news, list):
        logger.error(f"Data in {file_path} is not a list .")
        return []

    if not news:
        logger.warning(f"No news found in {file_path}.")
        return []

    chunks =[]

    for idx, news_item in enumerate(news):
        if not isinstance(news_item, dict):
            logger.warning(f"Record at index {idx} is not a dict. Skipping.")
            continue

        news_id =news_item.get("id","")
        news_title = news_item.get("title","")
        news_excerpt = news_item.get("excerpt","")
        news_content = news_item.get("content","")
        newcontent_text = html_to_text(news_content) # chuyển html content sang text
        news_content_split = split_paragraphs(newcontent_text)
        news_image= news_item.get("thumbnailUrl","")    
        news_category = news_item.get("category",{})

        base_metadata = {
                            "type": "news",
                            "source": "news.json",
                            "news_id": news_id,
                            "news_title": news_title,
                            "created_at": datetime.utcnow().isoformat(),
                            "language": "vi",
                        }

        CHUNK_PRIORITY = {
            "overview": 1,
            "content": 2,
            "category": 3,
        }

        # Chunk overview (title + excerpt + image)
        if news_title and news_excerpt:
            if news_image:
                chunks.append({
                    "text": f"Tin tức: {news_title}\nMô tả ngắn tin tức: {news_excerpt}\nHình ảnh đại diện: {news_image}",
                    "metadata": make_metadata(base_metadata, chunk_type="overview", priority=CHUNK_PRIORITY["overview"])
                })
            else:
                chunks.append({
                    "text": f"Tin tức: {news_title}\nMô tả ngắn tin tức: {news_excerpt}\n",
                    "metadata": make_metadata(base_metadata, chunk_type="overview", priority=CHUNK_PRIORITY["overview"])
                })

        # Chunk content paragraphs
        for idx, paragraph in enumerate(news_content_split):
            if paragraph.strip():
                chunks.append({
                    "text": paragraph.strip(),
                    "metadata": make_metadata(base_metadata, chunk_type="content", priority=CHUNK_PRIORITY["content"], paragraph_index=idx)
                })

        # Chunk category
        if news_category:
            category_name = news_category.get("name", "")
            chunks.append({
                "text": f"Chuyên mục tin tức: {category_name}",
                "metadata": make_metadata(base_metadata, chunk_type="category", priority=CHUNK_PRIORITY["category"])
            })

    return chunks
