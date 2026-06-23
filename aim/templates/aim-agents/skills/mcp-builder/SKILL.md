---
name: mcp-builder
description: Lays out the principles for building Model Context Protocol servers — how to shape tools, expose resources, pick a transport, handle errors and secrets, and stay current with the spec. It favors design reasoning over framework-specific boilerplate so the ideas carry to either the TypeScript or Python SDK. Use it when standing up an MCP server, designing its tools, or modeling its resources.
---

# Building MCP Servers

The Model Context Protocol is the wiring that lets an AI system reach external tools and data through a stable contract. A well-built server makes that contract obvious; a poorly built one leaves the model guessing. The notes below are about getting the design right.

## The Three Building Blocks

A server exposes some mix of three things:

| Block | What it gives the model |
|-------|------------------------|
| Tools | Functions it can call to act |
| Resources | Data it can read |
| Prompts | Reusable prompt templates |

## Laying Out The Server

### A minimal project

```
my-server/
├── src/
│   └── index.ts      # entry — McpServer from the TS SDK
├── package.json      # depends on @modelcontextprotocol/sdk
└── tsconfig.json
```

The TypeScript SDK is `@modelcontextprotocol/sdk`, which exports `McpServer`. The Python SDK is the `mcp` package — install it with `pip install "mcp[cli]"`, and reach for `FastMCP` from `mcp.server.fastmcp`.

### Transports

| Transport | Where it fits |
|-----------|--------------|
| stdio | Local processes, CLI-launched servers |
| Streamable HTTP | Remote and web-hosted servers (this superseded the old HTTP+SSE transport) |

The current spec (revision 2025-06-18) standardizes exactly these two. WebSocket is not a standard transport. On any Streamable HTTP server, check the `Origin` header before trusting a request.

## Designing Tools

### What a good tool looks like

| Trait | What it means |
|-------|--------------|
| Verb-first name | `fetch_invoice`, `archive_thread` — the action is in the name |
| One job | It does a single thing and does it cleanly |
| Typed input | A schema with types and per-field descriptions |
| Predictable output | A consistent, parseable result shape |

### Shaping the input schema

| Piece | Needed? |
|-------|---------|
| Top-level type | Yes — `object` |
| Properties | Define every parameter |
| Required list | Name the mandatory ones |
| Descriptions | Write them for a human reader |

## Designing Resources

### Kinds of resource

| Kind | When to use it |
|------|---------------|
| Static | Data that doesn't change — config, docs |
| Dynamic | Produced fresh on each request |
| Templated | A URI carrying parameters |

### URI shapes

| Shape | Example |
|-------|---------|
| Fixed | `docs://changelog` |
| Parameterized | `tickets://{ticketId}` |
| Collection | `assets://project/*` |

## Handling Errors

### What to return when

| Situation | Response |
|-----------|----------|
| Bad input | A validation message that says what's wrong |
| Missing target | A plain "not found" |
| Internal failure | A generic error to the caller, full detail to the log |

### Principles

- Return errors as structured data, not bare strings.
- Never leak internals — stack traces, queries, secrets — to the caller.
- Log enough to debug later.
- Make every message actionable.

## Multimodal Returns

| Type | How it's carried |
|------|-----------------|
| Text | Plain text |
| Image | Base64 plus a MIME type |
| File | Base64 plus a MIME type |

## Staying Secure

### Inputs

- Validate everything a tool receives.
- Sanitize anything a user supplied.
- Scope what a resource can reach.

### Secrets

- Read keys from the environment, never hardcode them.
- Keep secrets out of the logs.
- Check permissions before acting on them.

## Wiring Up Clients

### Local server config

| Field | Purpose |
|-------|---------|
| command | The executable to launch (stdio servers) |
| args | Arguments passed to it |
| env | Environment variables to set |

MCP is host-agnostic: one server works the same across desktop assistants, coding tools, and IDE hosts. A remote Streamable HTTP server authenticates over OAuth instead of being launched by a local command.

## Spec Features Worth Using

From revision 2025-06-18, these earn their place in a modern server:

| Feature | What it buys you |
|---------|-----------------|
| Tool annotations | Signal read-only versus destructive behavior to the host |
| `outputSchema` / structured content | Typed, predictable results |
| Resource links | Hand back references to resources from a tool result |
| OAuth | Authentication for remote / Streamable HTTP servers |

## Testing

| Layer | What it checks |
|-------|---------------|
| Unit | The logic inside a tool |
| Integration | The server end to end |
| Contract | Schemas match what's promised |

## Pre-Ship Checklist

- [ ] Tool names are verbs and read clearly
- [ ] Every input schema is complete and described
- [ ] Outputs are structured JSON
- [ ] Errors are handled on every path
- [ ] All inputs are validated
- [ ] Configuration comes from the environment
- [ ] Logging is in place for debugging

The model leans entirely on your descriptions to call a tool correctly. Keep each tool small, single-purpose, and thoroughly documented, and it will use them well.
