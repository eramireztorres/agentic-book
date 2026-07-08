"""Retrieval evaluation profile defaults."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from agentic_book.domain.models import RetrievalEvalProfileName, RetrievalMode

ThresholdName = Literal["min_hit_rate", "min_mrr", "min_unanswerable_success", "min_score"]
MatrixRowName = Literal["baseline", "vector", "guarded"]


@dataclass(frozen=True)
class RetrievalEvalProfile:
    name: RetrievalEvalProfileName
    retrieval_mode: RetrievalMode
    min_hit_rate: float
    min_mrr: float
    min_unanswerable_success: float
    min_score: float


@dataclass(frozen=True)
class RetrievalEvalMatrixRow:
    name: MatrixRowName
    profile: RetrievalEvalProfileName
    retrieval_mode: RetrievalMode | None = None
    min_hit_rate: float | None = None
    min_mrr: float | None = None
    min_unanswerable_success: float | None = None
    min_score: float | None = None


_RETRIEVAL_EVAL_PROFILES: dict[RetrievalEvalProfileName, RetrievalEvalProfile] = {
    "baseline": RetrievalEvalProfile(
        name="baseline",
        retrieval_mode="lexical",
        min_hit_rate=1.0,
        min_mrr=0.8,
        min_unanswerable_success=1.0,
        min_score=0.0,
    ),
    "guarded": RetrievalEvalProfile(
        name="guarded",
        retrieval_mode="hybrid",
        min_hit_rate=1.0,
        min_mrr=0.8,
        min_unanswerable_success=1.0,
        min_score=0.02,
    ),
    "custom": RetrievalEvalProfile(
        name="custom",
        retrieval_mode="lexical",
        min_hit_rate=1.0,
        min_mrr=0.8,
        min_unanswerable_success=0.0,
        min_score=0.0,
    ),
}


def get_retrieval_eval_profile(name: RetrievalEvalProfileName) -> RetrievalEvalProfile:
    return _RETRIEVAL_EVAL_PROFILES[name]


def list_retrieval_eval_profiles() -> tuple[RetrievalEvalProfile, ...]:
    return tuple(_RETRIEVAL_EVAL_PROFILES.values())


def list_retrieval_eval_matrix_rows() -> tuple[RetrievalEvalMatrixRow, ...]:
    return (
        RetrievalEvalMatrixRow(name="baseline", profile="baseline"),
        RetrievalEvalMatrixRow(
            name="vector",
            profile="custom",
            retrieval_mode="vector",
            min_hit_rate=0.9,
            min_mrr=0.6,
            min_unanswerable_success=0.0,
        ),
        RetrievalEvalMatrixRow(name="guarded", profile="guarded"),
    )


def resolve_retrieval_eval_row(row: RetrievalEvalMatrixRow) -> RetrievalEvalProfile:
    profile = get_retrieval_eval_profile(row.profile)
    return RetrievalEvalProfile(
        name=row.profile,
        retrieval_mode=row.retrieval_mode or profile.retrieval_mode,
        min_hit_rate=row.min_hit_rate if row.min_hit_rate is not None else profile.min_hit_rate,
        min_mrr=row.min_mrr if row.min_mrr is not None else profile.min_mrr,
        min_unanswerable_success=(
            row.min_unanswerable_success
            if row.min_unanswerable_success is not None
            else profile.min_unanswerable_success
        ),
        min_score=row.min_score if row.min_score is not None else profile.min_score,
    )
