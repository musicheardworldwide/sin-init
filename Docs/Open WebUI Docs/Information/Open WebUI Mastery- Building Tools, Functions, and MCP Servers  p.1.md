## 📦 Part 1: Tools – Creating Callable Functions for LLMs

[[sin/Initialization/Docs/Open WebUI Docs/Open WebUI tools|Open WebUI tools]] [[Tools]] are structured Python plugins that LLMs can invoke during chats. These [[Tools]] are bound to specific [[sin/Initialization/Docs/Datasets/8. Datasets]] that support **function calling**, such as GPT-[[tools-export-1745623456262.json]] or Claude.

### 📁 Tool Structure

Every tool lives inside a single `.py` file, with:

* A top-level docstring describing metadata
* A `[[[[Tools]]]]` class
* Optional `Valves` and `UserValves` for settings

#### ✅ Example: Basic String Reversal Tool

```python
"""title: String Reverser
author: Open WebUI Specialist
description: A tool that reverses a string.
required_open_webui_version: 0.6.0
version: 1.0.0
"""
from pydantic import BaseModel, Field
class Tools:
    class Valves(BaseModel):
        api_key: str = Field("", description="API key if required")
    def __init__(self):
        self.valves = self.Valves()
    def reverse_string(self, text: str) -> str:
        if self.valves.api_key and self.valves.api_key != "1234":
            return "Unauthorized"
        return text[::-1]
```

### 💡 Tool Setup Best Practices

* Add all metadata to the docstring to support import/export.
* Always validate input parameters (e.g., API keys).
* Use `Valves` for shared config.
* Add descriptions for [[sin/Initialization/Docs/Datasets/8. Datasets]] understanding.

### ⚙️ Import & Enable in Open WebUI

[[tools-export-1745623456262.json]]. Import from the [[sin/Initialization/Docs/Open WebUI Docs/Open WebUI tools|Open WebUI tools]]: **Workspace > [[Tools]] > Import Tool**
[[02-05-2025]]. Assign to [[sin/Initialization/Docs/Datasets/8. Datasets]] in **Workspace > [[sin/Initialization/Docs/Datasets/8. Datasets]] > [[Tools]]**
[[tools-export-1745623456262.json]]. Optionally use the `autotool_filter` for automatic function routing.

---

## 🎛️ Part 2: Pipe Functions – Defining Custom Model Logic

A **Pipe** defines a model route with custom business logic. It's useful for model orchestration, OpenAI proxying, or even scripted agents.

### 🔧 Barebones Pipe Example

```python
from pydantic import BaseModel, Field
class Pipe:
    class Valves(BaseModel):
        MODEL_ID: str = Field(default="debug-model")
    def __init__(self):
        self.valves = self.Valves()
    def pipe(self, body: dict):
        print("Incoming body:", body)
        return f"Received input: {body.get('messages', [{}])[-1].get('content', '')}"
```

### 🧪 Manifold Setup (Multiple Models)

You can define multiple models using `pipes()`:

```python
def pipes(self):
    return [
        {"id": "alpha", "name": "Alpha Bot"},
        {"id": "beta", "name": "Beta Bot"}
    ]
```

This lets you expose multiple "model options" from one Pipe.

---

## 🧰 Part 3: MCP Servers – Wrapping Legacy Tools as OpenAPI

Sometimes, tools are implemented in MCP. Open WebUI allows you to proxy them using the `mcpo` tool.

### 🔁 Convert MCP to OpenAPI with `mcpo`

**Quickstart:**

```bash
pip install mcpomcpo
uvx mcpo --port 8000 -- uvx mcp-server-time --local-timezone=America/New_York
```

Now you can access the OpenAPI docs at http://localhost:8000/docs and connect the server in Open WebUI under **Settings > Tools**.

### 🔐 Common Pitfalls

* Add **CORS middleware** if testing locally via browser:

  ```python
  from fastapi.middleware.cors import CORSMiddleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_methods=["*"],
      allow_headers=["*"]
  )
  ```
* Ensure your local tool uses HTTPS when Open WebUI is served over HTTPS, or run both on `localhost`.

---