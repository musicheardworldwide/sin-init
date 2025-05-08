# 🧠 Open WebUI Mastery: Building Tools, Functions, and MCP Servers (Page 2)

---

## 🎨 Part 4: Filters – Modify Inputs, Streamed Outputs, and Final Outputs

**Filters** let you intercept, rewrite, or polish data at 3 different stages of a chat:
Stage Function Purpose Before LLM `inlet` Modify user's prompt before it's sent During LLM `stream` Modify live streamed chunks After LLM `outlet` Modify full completed response

### ✨ Basic Filter Skeleton

```python
from pydantic import BaseModel
class Filter:
    class Valves(BaseModel):
        rewrite_prefix: str = "User said:"
    def __init__(self):
        self.valves = self.Valves()
    def inlet(self, body: dict) -> dict:
        body['messages'][-1]['content'] = f"{self.valves.rewrite_prefix} {body['messages'][-1]['content']}"
        return body
    def stream(self, event: dict) -> dict:
        # Modify mid-stream text here
        return event
    def outlet(self, body: dict) -> None:
        # Optionally log or clean final output
        print("Final Output:", body)
```

---

### 🔥 Real-World Filter Examples

* **Input Guardrails**: Detect offensive content before it goes to the LLM.
* **Stream Adjustments**: Strip unwanted tokens like `[smiles]`.
* **Outlet Redactions**: Mask sensitive outputs like emails or phone numbers.

### 📢 Tips When Building Filters

* Always validate your input dictionary structure (`body.get('messages', [])[-1].get('content', '')`).
* Filters run **fast** and **often**; keep `stream()` extremely lightweight.
* Filters are optional—returning unchanged body/event is fine.

---

## 🎬 Part 5: Action Functions – Adding Interactive Buttons in Chat

**Actions** insert a custom button under any user or AI message.
Think of Actions as:  
🔘 **Button ➔ Event Call ➔ User Interaction**

---

### 📜 Basic Action Example

```python
async def action(
    self,
    body: dict,
    __user__=None,
    __event_emitter__=None,
    __event_call__=None
) -> dict:
    response = await __event_call__({
        "type": "input",
        "data": {
            "title": "Custom Reply",
            "message": "Please write a reply",
            "placeholder": "Type something..."
        }
    })
    return {"user_input": response.get('text', '')}
```

**Key Points:**

* `__event_call__` prompts the user.
* You can chain multiple events (`input`, `confirm`, `select`).
* Action results are posted back into the conversation automatically.

---

### 🔗 Action Types Available

* `input`: Get a text input
* `confirm`: Yes/No
* `select`: Choose from dropdown options
* `download`: Trigger download of data
* `visualize`: Display structured visual graphs

---

## 🛠️ Part 6: Connecting OpenAPI Tool Servers Natively (Post-0.6.0)

Since Open WebUI v0.6+, you can connect **any** OpenAPI-compliant server directly.

---

### 🚀 Steps to Connect a Local OpenAPI Tool Server

1. Start your server (FastAPI, Flask, Express, etc.)
2. Ensure you have **CORS headers enabled**:

   ```python
   from fastapi.middleware.cors import CORSMiddleware
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"]
   )
   ```
3. Open Open WebUI → **Settings → Tools** ➕
4. Add your tool server URL (e.g., `http://localhost:8000`)
5. Save. Done!

---

### 🌐 Native Tool Calling (ReACT)

To use **function calling** natively inside chats:

* Open a chat
* ⚙️ Advanced Params → Set "Function Calling" ➔ `Native`
* Now Open WebUI will **auto-call functions** when prompted!

> **Note**: Your models need to truly support OpenAI-style function calling (e.g., GPT-4-turbo, Claude 3 Opus).

---

## 🚨 Common Problems & Fixes

Problem Cause Fix ❌ [[Tools]] don't show up Wrong OpenAPI spec or missing `/openapi.json` Check server `/docs` page manually ❌ CORS Error No CORS headers added Use `CORSMiddleware` or equivalent ❌ "Mixed Content" Error HTTPS [[sin/1. Initialization/Docs/Open WebUI Docs/Open WebUI tools|Open WebUI tools]] talking to HTTP server Serve tool server over HTTPS locally or tunnel via ngrok ❌ Function not triggered Model doesn't support native [[Functions]] Switch to GPT-4o, GPT-[[tools-export-1745623456262.json]] Turbo, or Claude [[tools-export-1745623456262.json]]