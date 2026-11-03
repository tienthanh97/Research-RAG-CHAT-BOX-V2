import logging
import os
from core.load_settings import load_settings
from retrieval.retriever import retrieve
from llm.generator import generate_answer

settings = load_settings()
logger = logging.getLogger("chat")

# Lấy giới hạn độ dài câu hỏi từ biến môi trường, mặc định là 512 ký tự
MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", "512"))

def chat(question: str) -> str:
    # 1. Kiểm tra tính hợp lệ của câu hỏi (Validation)
    if not question:
        logger.warning("Received empty question.")
        return "Câu hỏi không được để trống. Vui lòng nhập câu hỏi của bạn."

    if len(question) > MAX_QUERY_LENGTH:
        logger.warning("Question length exceeds maximum limit.")
        return f"Câu hỏi vượt quá độ dài tối đa cho phép là {MAX_QUERY_LENGTH} ký tự."

    logger.info(f"Starting retrieval for the question: {question}")

    try:
        # 2. Bước Truy xuất (Retrieval)
        # Tìm kiếm các tài liệu liên quan nhất trong Database vector
        documents = retrieve(question)

        # Nếu không tìm thấy tài liệu nào liên quan
        if not documents:
            logger.info("No relevant documents found.")
            return "Tôi không tìm thấy thông tin phù hợp trong dữ liệu hiện có."

        # 3. Xây dựng ngữ cảnh (Context Building)
        # Ghép các đoạn văn bản tìm được thành một chuỗi văn bản duy nhất (Context)
        # để gửi cho AI. Mỗi đoạn sẽ được đánh số [1], [2]... và đính kèm nguồn (metadata).
        context = "\n\n".join(
            f"[{i+1}] Nội dung context {i+1}\n{doc.text}\nNguồn: {doc.metadata}"
            for i, doc in enumerate(documents)
        )

        # 4. Bước Sinh câu trả lời (Generation)
        # Gửi câu hỏi + ngữ cảnh vừa xây dựng được vào mô hình LLM (Ollama/OpenAI)
        answer = generate_answer( context,question)

        logger.info("Answer generated successfully.")
        return answer

    except Exception as e:
        # 5. Xử lý lỗi hệ thống (Error Handling)
        logger.error(f"Error during retrieval: {e}")
        return "Đã xảy ra lỗi trong quá trình truy xuất thông tin. Vui lòng thử lại sau."

    
def main():
    while True:
        question = input("Bạn: ")
        if question.lower() in {"exit", "quit"}:
            print("Kết thúc cuộc trò chuyện.")
            break
            
        answer = chat(question)
        print(f"Bot: {answer}")

if __name__ == "__main__":
    main()
