"""Pure domain models.

The domain layer deliberately avoids dependencies on MCP, vector stores, cloud
SDKs, and filesystem-specific concepts. Paths and buckets belong in adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Literal

ContentLayer = Literal["canonical", "wiki"]
DocumentStatus = Literal["draft", "reviewed", "deprecated"]
DocumentType = Literal[
    "concept",
    "pattern",
    "platform",
    "playbook",
    "case-study",
    "checklist",
    "risk",
    "tool",
    "standard",
    "glossary",
]
Maturity = Literal["experimental", "emerging", "production", "legacy"]
SourceQuality = Literal["primary", "curated", "community", "vendor", "internal"]
SourceType = Literal["official", "vendor", "community", "internal", "derived"]
ChangeFrequency = Literal["low", "medium", "high", "volatile"]
RetrievalMode = Literal["lexical", "vector", "hybrid"]
RetrievalEvalProfileName = Literal["baseline", "guarded", "custom"]


@dataclass(frozen=True)
class ContentObjectRef:
    """Backend-neutral reference to a content object."""

    uri: str
    layer: ContentLayer = "canonical"


@dataclass(frozen=True)
class ContentObject:
    """Backend-neutral content object loaded from filesystem, S3, or another store."""

    ref: ContentObjectRef
    text: str


@dataclass(frozen=True)
class DocumentMetadata:
    id: str
    title: str
    type: DocumentType
    domain: list[str]
    audience: list[str]
    maturity: Maturity
    status: DocumentStatus
    last_reviewed: date
    source_quality: SourceQuality
    source_urls: list[str] = field(default_factory=list)
    source_type: SourceType | None = None
    upstream_version: str | None = None
    last_checked: date | None = None
    review_after: date | None = None
    change_frequency: ChangeFrequency | None = None
    supersedes: list[str] = field(default_factory=list)
    superseded_by: str | None = None
    tags: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)
    layer: ContentLayer = "canonical"


@dataclass(frozen=True)
class Section:
    id: str
    document_id: str
    heading: str
    level: int
    text: str
    heading_path: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Document:
    metadata: DocumentMetadata
    body: str
    source_uri: str
    sections: list[Section] = field(default_factory=list)


@dataclass(frozen=True)
class Chunk:
    id: str
    document_id: str
    text: str
    kind: Literal["document", "section"]
    source_uri: str
    metadata: DocumentMetadata
    section_id: str | None = None
    section_heading: str | None = None
    content_hash: str | None = None


@dataclass(frozen=True)
class RetrievalFilters:
    type: list[str] = field(default_factory=list)
    domain: list[str] = field(default_factory=list)
    audience: list[str] = field(default_factory=list)
    maturity: list[str] = field(default_factory=list)
    status: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    layer: list[ContentLayer] = field(default_factory=lambda: ["canonical"])


@dataclass(frozen=True)
class RetrievalQuery:
    query: str
    top_k: int = 8
    retrieval_mode: RetrievalMode = "hybrid"
    filters: RetrievalFilters = field(default_factory=RetrievalFilters)


@dataclass(frozen=True)
class RetrievalResult:
    result_id: str
    document_id: str
    chunk_id: str
    title: str
    score: float
    source_uri: str
    text: str
    metadata: DocumentMetadata
    retrieval_mode: str
    section_heading: str | None = None
    why_retrieved: str | None = None


@dataclass(frozen=True)
class RetrievalEvalCase:
    id: str
    query: str
    expected_document_ids: list[str] = field(default_factory=list)
    top_k: int = 5
    tags: list[str] = field(default_factory=list)
    notes: str | None = None

    @property
    def answerable(self) -> bool:
        return bool(self.expected_document_ids)


@dataclass(frozen=True)
class RetrievalEvalResult:
    case_id: str
    query: str
    expected_document_ids: list[str]
    retrieved_document_ids: list[str]
    hit: bool
    reciprocal_rank: float
    top_k: int
    abstained: bool = False
    max_score: float = 0.0


@dataclass(frozen=True)
class RetrievalEvalReport:
    profile: RetrievalEvalProfileName
    cases: int
    answerable_cases: int
    unanswerable_cases: int
    hit_rate: float
    mean_reciprocal_rank: float
    unanswerable_success_rate: float
    retrieval_mode: RetrievalMode = "lexical"
    min_score: float = 0.0
    abstention_rate: float = 0.0
    results: list[RetrievalEvalResult] = field(default_factory=list)


@dataclass(frozen=True)
class ValidationIssue:
    source_uri: str
    message: str
    severity: Literal["error", "warning"] = "error"


@dataclass(frozen=True)
class ValidationReport:
    documents_checked: int
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)


@dataclass(frozen=True)
class IngestionReport:
    documents_seen: int
    chunks_planned: int
    dry_run: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    documents_indexed: int = 0
    chunks_indexed: int = 0
    documents_changed: int = 0
    documents_unchanged: int = 0
    documents_removed: int = 0
    manifest_uri: str | None = None


@dataclass(frozen=True)
class IngestionManifest:
    schema_version: str
    storage_backend: str
    index_backend: str
    documents: int
    chunks: int


@dataclass(frozen=True)
class DocumentIngestionRecord:
    document_id: str
    source_uri: str
    source_hash: str


@dataclass(frozen=True)
class IngestionState:
    schema_version: str
    documents: list[DocumentIngestionRecord] = field(default_factory=list)


@dataclass(frozen=True)
class StaleDocument:
    document_id: str
    title: str
    source_uri: str
    review_after: date | None
    change_frequency: ChangeFrequency | None
    days_overdue: int | None
    reason: str


@dataclass(frozen=True)
class StaleReport:
    checked: int
    stale: list[StaleDocument] = field(default_factory=list)


@dataclass(frozen=True)
class DocumentationUpdateProposal:
    id: str
    document_id: str
    reason: str
    status: Literal["draft", "needs-human-review", "accepted", "rejected"]
    created_on: date
    source_hint: str | None = None
    urgency: Literal["low", "medium", "high"] = "medium"
    proposed_change: str | None = None
