import logging
import math
import re
from collections import Counter

logger = logging.getLogger("embedding")


# Nhanh ve 1 doan text thanh 1 list cac token cua keyword
def tokenize(text: str) -> list[str]:
    if not text:
        logger.warning(
            "Empty text received for tokenization in sparse_embedder.")
        return []

    text = text.lower()  # Chuyen thanh chu thuong de giam so luong token khac nhau. VD: "Apple" va "apple" se duoc xem la giong nhau
    # Xoa ky tu dac biet. VD: "hello, world!" -> "hello world"
    text = re.sub(r'[^\w\s]', ' ', text)
    # [^\w\s] la lieu thuc chinh quy de tim kieu ky tu khong phai chu cai hoac khoang trang
    tokens = text.split()
    return tokens


class SparseEmbedder:
    def __init__(self):
        # Tu dien de luu tru cac token va chi so tuong ung chung
        self.vocabulary: dict[str, int] = {}
        # Dem so luong van ban chua token do
        self.document_frequency: Counter = Counter()
        self.num_documents = 0  # Tong so van ban da duoc dung de fit model

    def __update_vocabulary(self, tokens: list[str]):
        for token in set(tokens):
            self.document_frequency[token] += 1
            if token not in self.vocabulary:
                self.vocabulary[token] = len(self.vocabulary)

    def fit(self, texts: list[str]):
        self.num_documents = len(texts)
        for text in texts:
            tokens = tokenize(text)
            self.__update_vocabulary(tokens)
        logger.info(
            f"Fitted SparseEmbedder with {self.num_documents} documents and vocabulary size {len(self.vocabulary)}.")

    def __inverse_document_frequency(self, token: str) -> float:
        document_frequency = self.document_frequency.get(token, 0)
        return math.log((self.num_documents + 1) / (document_frequency + 1)) + 1

    def encode(self, text: str) -> dict[int, list[float]]:
        tokens = tokenize(text)
        if not tokens:
            return {"indices": [], "values": []}

        # tra ve so luong token xuat hien trong text
        term_frequency = Counter(tokens)
        indices = []
        values = []

        for term, frequency in term_frequency.items():
            if not term in self.vocabulary:
                logger.warning(f"Token '{term}' not in vocabulary. Skipping.")
                continue

            term_id = self.vocabulary[term]
            weight = frequency * self.__inverse_document_frequency(term)

            indices.append(term_id)
            values.append(weight)

        return {"indices": indices, "values": values}

    def encode_batch(self, texts: list[str]) -> list[dict[int, list[float]]]:
        return [self.encode(text) for text in texts]
