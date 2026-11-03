import logging

logger = logging.getLogger("ingestion")

# Truong hop 1, neu co dau cham truoc do thi minh cat o dau cham do
# Truong hop 2, neu khong co dau cham truoc do thi minh cat o vi tri max_len
# Neu < max_len
# Thi minh khai bao 1 buffer, va them doan van vao buffer
# buffer = 0 + doan van
# buffer + doan van moi > max_len

def split_paragraphs(text: str, max_len:400):
    if not text:
        logger.warning("Empty text provided to split_paragraphs")
        return []
    
    sentences = text.split(". ")
    out = [] # list cac chunk
    buf = "" # buffer de ghep cac cau nho

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            logger.warning("Empty sentence after stripping")
            continue
            
        while len(sentence) > max_len:
            cut = sentence.rfind(". ", 0, max_len)
            if cut == -1:
                cut = max_len
            
            chunk = sentence[:cut].strip()
            if chunk:
                out.append(chunk)
            
            sentence = sentence[cut:].strip()

        if len(buf) + len(sentence) + 2 <= max_len: # ly do +2: de tinh dau ". "
            buf += sentence + ". "
        else:
            out.append(buf.strip())
            buf = sentence + ". "

    if buf:
        out.append(buf.strip())

    return out
