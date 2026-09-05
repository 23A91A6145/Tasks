import re
import math
from typing import List, Tuple, Dict
from backend.app.models.schemas import EvidenceChunk

class BM25Retriever:
    """Lightweight BM25 Lexical Keyword Retriever."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus: List[EvidenceChunk] = []
        self.doc_len: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: List[Dict[str, int]] = []
        self.idf: Dict[str, float] = {}

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\w+", text.lower())

    def index(self, chunks: List[EvidenceChunk]):
        self.corpus = chunks
        self.doc_len = [len(self._tokenize(c.content)) for c in chunks]
        self.avg_doc_len = sum(self.doc_len) / len(self.doc_len) if self.doc_len else 1.0
        
        df: Dict[str, int] = {}
        self.doc_freqs = []
        for chunk in chunks:
            tokens = self._tokenize(chunk.content)
            tf: Dict[str, int] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self.doc_freqs.append(tf)
            for t in tf:
                df[t] = df.get(t, 0) + 1
                
        N = len(chunks)
        self.idf = {
            t: math.log((N - freq + 0.5) / (freq + 0.5) + 1.0)
            for t, freq in df.items()
        }

    def search(self, query: str, top_k: int = 5) -> List[Tuple[EvidenceChunk, float]]:
        if not self.corpus:
            return []
        query_tokens = self._tokenize(query)
        scores: List[Tuple[EvidenceChunk, float]] = []
        
        for idx, chunk in enumerate(self.corpus):
            score = 0.0
            doc_len = self.doc_len[idx]
            tf_dict = self.doc_freqs[idx]
            
            for t in query_tokens:
                if t in tf_dict:
                    freq = tf_dict[t]
                    numerator = freq * (self.k1 + 1)
                    denominator = freq + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
                    score += self.idf.get(t, 0.0) * (numerator / denominator)
            scores.append((chunk, score))
            
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
