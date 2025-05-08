Here’s a developer-focused breakdown of what makes an **OpenWebUI-compatible [[sin/1. Initialization/Docs/MCP|MCP]] server** stand out, based on `mcpo`’s design and OpenWebUI’s ecosystem:

---

### **1. Core Principles for OpenWebUI Acceptance**

#### **(A) Protocol Agnosticism**

- **MCP-to-OpenAPI Bridge**:

  `mcpo` solves the critical gap between MCP’s stdio-based tools and RESTful OpenAPI expectations. Your server should:
  - **Support both MCP (stdio) and OpenAPI (HTTP)** interfaces natively, or use `mcpo` as a proxy.
  - **Expose standardized endpoints** (e.g., `/docs`, `/health`) for discoverability.

#### **(B) Zero-Config Interoperability**

- **Auto-Generated OpenAPI Schemas**:

  OpenWebUI tools rely on schema introspection. Use frameworks like FastAPI to auto-generate:

  ```python
  
  app = FastAPI(title="My Server", version="1.0.0")  # ← Metadata matters!
  
  ```
  - **Tag endpoints** (e.g., `@app.post("/search", tags=["RAG"])` for UI grouping.

---

### **2. Key Technical Requirements**

#### **(A) Security**

- **Mandatory**:
  - **API Keys**: Inject via `--api-key` (like `mcpo`’s `--api-key "top-secret"`).
  - **CORS**: Restrict to OpenWebUI’s default origins (e.g., `http://localhost:3000`).
  - **Input Sanitization**: Normalize paths/IDs (e.g., prevent SQLi or path traversal).
- **Recommended**:
  - **RBAC**: Use OpenWebUI’s JWT tokens for role-based access control.

#### **(B) Stateless Design**

- **Sessionless Operations**:

  OpenWebUI agents expect idempotent APIs. Avoid server-side state; use:
  - **Client-provided context** (e.g., `user_id` in headers).
  - **Atomic transactions** (e.g., `POST /edit_file` with full content replacement).

#### **(C) Performance**

- **Async I/O**:

  FastAPI’s async endpoints (`async def`) for concurrent requests.
- **SSE Support**:

  For streaming (e.g., LLM responses), implement Server-Sent Events:

  ```bash
  
  mcpo --server-type "sse" -- http://127.0.0.1:8001/sse  # ← SSE proxy example
  
  ```

---

### **3. Integration Patterns**

#### **(A) MCP Server Requirements**

- **Stdio Interface**:

  Your tool must handle MCP’s JSON-over-stdin protocol:

  ```json
  
  {"command": "search", "params": {"query": "AI"}}
  
  ```
- **Exit Codes**: Return `0` on success, non-zero for errors (mapped to HTTP status codes by `mcpo`).

#### **(B) OpenAPI Best Practices**

- **Use Pydantic Models**:

  For input/output validation (like the filesystem server’s `EditFileRequest`).
- **Standard Endpoints**:

  | Endpoint          | Purpose                          |

  |-------------------|----------------------------------|

  | `GET /health`     | Service liveness check           |

  | `GET /openapi.json` | Schema export (auto-generated)   |

  | `POST /execute`   | Generic MCP command proxy        |

#### **(C) Configuration**

- **Environment Variables**:

  Mirror `mcpo`’s approach (e.g., `--port`, `--api-key`).
- **Config Files**:

  Support JSON configs for multi-tool setups (like `mcpo`’s `config.json`).

---

### **4. DevEx Optimization**

#### **(A) Debugging**

- **Interactive Docs**:

  FastAPI’s `/docs` and `/redoc` endpoints are auto-proxied by `mcpo`.
- **Logging**:

  Structured logs (JSON) with request IDs for tracing.

#### **(B) Testing**

- **Pytest Fixtures**:

  Mock MCP stdio streams (input/output/error).

  ```python
  
  def test_mcp_command(mcp_server):
  
      result = mcp_server.execute('{"command": "ping"}')
  
      assert result == {"status": "ok"}
  
  ```

#### **(C) Deployment**

- **Docker Support**:

  Provide a `Dockerfile` with multi-stage builds (like `mcpo`’s image).
- **uv Compatibility**:

  Use `uvx` for fast startup (critical for serverless/edge).

---

### **5. What OpenWebUI Rejects**

- **Custom Protocols**:

  Avoid non-HTTP transports (WebSockets, gRPC) unless proxied via `mcpo`.
- **Stateful APIs**:

  Servers requiring long-lived sessions (e.g., WebSocket chat) need SSE adaptation.
- **Hardcoded Secrets**:

  Never embed API keys—use env vars or mounts.

---

### **6. Reference Implementation**

Study these `mcpo`-compatible servers:

1. [**Filesystem Server**](https://github.com/open-webui/openapi-servers/blob/main/filesystem-server/server.py)
   - FastAPI + Pydantic
   - Path sanitization
   - Atomic writes
2. [**Knowledge Graph Server**](https://github.com/open-webui/openapi-servers/blob/main/knowledge-graph-server/server.py)
   - JSONL persistence
   - Graph traversal API
   - SSE-ready
3. [**MCP Time Server**](https://github.com/open-webui/mcpo/blob/main/examples/mcp-server-time)
   - Minimal MCP stdio interface
   - Zero HTTP code (relies on `mcpo`)

---

### **7. Quickstart Checklist**

To ensure acceptance:

```bash

# 1. Build your MCP tool (stdio interface)

# 2. Proxy it with mcpo

uvx mcpo --port 8000 --config /app/config/config.json

# 3. Verify OpenAPI compliance

curl http://localhost:8000/openapi.json | jq '.info.title'

# 4. Integrate with OpenWebUI

#    → Set OPENAPI_SERVERS="http://localhost:8000" in OpenWebUI .env
```

By aligning with `mcpo`’s design, your server gains instant compatibility with OpenWebUI’s agent ecosystem—no custom integration needed.