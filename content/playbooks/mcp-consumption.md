---
id: "playbook.mcp-consumption"
title: "Consuming Agentic Book Through MCP"
type: "playbook"
domain: ["agents", "mcp", "operations"]
audience: ["agent", "engineer"]
maturity: "emerging"
status: "draft"
last_reviewed: "2026-06-30"
source_quality: "curated"
source_urls:
  - "docs/implementation-roadmap.md"
source_type: "derived"
upstream_version: "2026-06-30"
last_checked: "2026-06-30"
review_after: "2026-09-30"
change_frequency: "high"
supersedes: []
superseded_by: null
tags: ["mcp", "retrieval", "workflow"]
related:
  - "concept.mcp"
  - "platform.fastmcp"
---

# Consuming Agentic Book Through MCP

An agent should first inspect the corpus manifest, then search for relevant
sections, and finally retrieve complete documents when it needs full context.

## Recommended Flow

1. Call `corpus_manifest`.
2. Call `search` or `fusion_search`.
3. Call `get_document` for the strongest evidence.
