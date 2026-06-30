"""Retrieval use cases."""

from __future__ import annotations

from dataclasses import replace

from agentic_book.application.fusion import reciprocal_rank_fusion
from agentic_book.domain.models import RetrievalQuery, RetrievalResult
from agentic_book.domain.ports import EmbeddingProvider, LexicalIndex, VectorStore


class SearchCorpus:
    def __init__(
        self,
        lexical_index: LexicalIndex,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: VectorStore | None = None,
        rrf_k: int = 60,
    ) -> None:
        self._lexical_index = lexical_index
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._rrf_k = rrf_k

    async def run(self, query: RetrievalQuery) -> list[RetrievalResult]:
        if query.retrieval_mode == "lexical":
            return await self._lexical_index.search(query)
        if query.retrieval_mode == "vector":
            return await self._vector_search(query)
        if query.retrieval_mode == "hybrid":
            return await self._hybrid_search(query)
        raise ValueError("retrieval_mode must be one of: lexical, vector, hybrid")

    async def _vector_search(self, query: RetrievalQuery) -> list[RetrievalResult]:
        if self._embedding_provider is None or self._vector_store is None:
            raise ValueError("Vector retrieval requires an embedding provider and vector store")
        query_vector = (await self._embedding_provider.embed_texts([query.query]))[0]
        return await self._vector_store.search(query, query_vector)

    async def _hybrid_search(self, query: RetrievalQuery) -> list[RetrievalResult]:
        lexical_query = replace(query, retrieval_mode="lexical")
        vector_query = replace(query, retrieval_mode="vector")
        lexical_results = await self._lexical_index.search(lexical_query)
        vector_results = await self._vector_search(vector_query)
        rankings = [
            [result.chunk_id for result in lexical_results],
            [result.chunk_id for result in vector_results],
        ]
        fused_scores = reciprocal_rank_fusion(rankings, k=self._rrf_k)
        best_result_by_chunk: dict[str, RetrievalResult] = {}
        sources_by_chunk: dict[str, list[str]] = {}
        for mode, results in (("lexical", lexical_results), ("vector", vector_results)):
            for result in results:
                current = best_result_by_chunk.get(result.chunk_id)
                if current is None or result.score > current.score:
                    best_result_by_chunk[result.chunk_id] = result
                sources_by_chunk.setdefault(result.chunk_id, []).append(mode)

        fused_results = [
            replace(
                best_result_by_chunk[chunk_id],
                result_id=f"hybrid::{chunk_id}",
                score=score,
                retrieval_mode="hybrid",
                why_retrieved="Fused retrieval modes: " + ", ".join(sorted(set(sources_by_chunk[chunk_id]))),
            )
            for chunk_id, score in fused_scores.items()
        ]
        fused_results.sort(key=lambda result: (-result.score, result.document_id, result.chunk_id))
        return fused_results[: query.top_k]
