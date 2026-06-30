---
id: "pattern.hybrid-retrieval"
title: "Hybrid Retrieval"
type: "pattern"
domain: ["rag", "retrieval"]
audience: ["engineer", "architect", "agent"]
maturity: "production"
status: "reviewed"
last_reviewed: "2026-06-30"
source_quality: "curated"
source_urls:
  - "docs/architecture-recommendations.md"
source_type: "derived"
upstream_version: "2026-06-30"
last_checked: "2026-06-30"
review_after: "2026-12-30"
change_frequency: "medium"
supersedes: []
superseded_by: null
tags: ["bm25", "vector-search", "rrf"]
related:
  - "concept.mcp"
---

# Hybrid Retrieval

Hybrid retrieval combines lexical search for exact terms with vector search for
semantic similarity.

## Agentic Book Baseline

The first production-oriented baseline should support lexical, vector, and hybrid
retrieval modes before adding GraphRAG, HyDE, or rerankers.
