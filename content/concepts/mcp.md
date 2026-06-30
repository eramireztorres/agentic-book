---
id: "concept.mcp"
title: "Model Context Protocol"
type: "concept"
domain: ["agents", "mcp"]
audience: ["engineer", "architect", "agent"]
maturity: "production"
status: "reviewed"
last_reviewed: "2026-06-30"
source_quality: "curated"
source_urls:
  - "https://modelcontextprotocol.io/docs"
source_type: "official"
upstream_version: "2026-06-18"
last_checked: "2026-06-30"
review_after: "2026-09-30"
change_frequency: "high"
supersedes: []
superseded_by: null
tags: ["tools", "resources", "prompts", "stdio", "streamable-http"]
related:
  - "platform.fastmcp"
  - "pattern.hybrid-retrieval"
---

# Model Context Protocol

MCP is the serving layer used by this project to expose agent-friendly resources,
tools, and prompts over local stdio or Streamable HTTP.

## Transports

Use stdio for local editor and desktop integrations. Use Streamable HTTP when the
server must be reachable as a local or remote endpoint.

## Surface Area

Agentic Book should expose tools for retrieval, resources for stable content, and
prompts for repeatable agent workflows.
