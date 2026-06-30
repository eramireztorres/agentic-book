---
id: "platform.fastmcp"
title: "FastMCP"
type: "platform"
domain: ["agents", "mcp", "python"]
audience: ["engineer", "agent"]
maturity: "production"
status: "reviewed"
last_reviewed: "2026-06-30"
source_quality: "curated"
source_urls:
  - "https://gofastmcp.com/"
source_type: "official"
upstream_version: "3.1.0"
last_checked: "2026-06-30"
review_after: "2026-09-30"
change_frequency: "high"
supersedes: []
superseded_by: null
tags: ["python", "mcp", "tools", "resources", "prompts"]
related:
  - "concept.mcp"
---

# FastMCP

FastMCP is the recommended Python-facing server framework for this scaffold's MCP
interface. It should remain an interface adapter, not a domain dependency.

## Usage Boundary

FastMCP tools call application use cases. They must not own parsing, indexing,
ranking, or storage logic.
