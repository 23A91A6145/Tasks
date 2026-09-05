import pytest
from backend.app.retrieval.keyword import BM25Retriever
from backend.app.retrieval.semantic import SemanticRetriever
from backend.app.retrieval.hybrid import HybridRRFRetriever
from backend.app.models.schemas import EvidenceChunk

def test_bm25_retrieval():
    retriever = BM25Retriever()
    chunks = [
        EvidenceChunk(id="c1", source_id="s1", content="LangGraph supports state checkpointing with PostgreSQL.", chunk_index=0),
        EvidenceChunk(id="c2", source_id="s2", content="CrewAI uses role-based agent coordination and memory.", chunk_index=0),
        EvidenceChunk(id="c3", source_id="s3", content="Docker containers provide isolated environments on Ubuntu.", chunk_index=0)
    ]
    retriever.index(chunks)
    results = retriever.search("checkpointing PostgreSQL", top_k=2)
    assert len(results) > 0
    assert results[0][0].id == "c1"

def test_hybrid_rrf_retrieval():
    hybrid = HybridRRFRetriever(k=60)
    chunks = [
        EvidenceChunk(id="c1", source_id="s1", content="LangGraph supports state checkpointing with PostgreSQL.", chunk_index=0),
        EvidenceChunk(id="c2", source_id="s2", content="CrewAI uses role-based agent coordination and memory.", chunk_index=0),
        EvidenceChunk(id="c3", source_id="s3", content="Model Context Protocol standardizes tool execution.", chunk_index=0)
    ]
    ranked = hybrid.search("Model Context Protocol tool execution", chunks, top_k=2)
    assert len(ranked) == 2
    assert ranked[0].id == "c3"
