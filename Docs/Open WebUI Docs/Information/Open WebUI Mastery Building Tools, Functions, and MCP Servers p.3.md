# 🧠 Open WebUI Mastery Building Tools, Functions, and MCP Servers 

---

## 🛡️ Part 7: Advanced Architecture – Managing Multiple Servers and Security

Now that you're building real systems, not just playing with local scripts, it's time to **level up**:

* Multi-server tool orchestration
* Secure production deployments
* JWT, Bearer Token, and CORS strategies

---

### 🏗️ Multi-Tool Server Architecture

🔵 **Why use multiple tool servers?**

* Keep tools modular and easy to update
* Scale servers independently
* Load balance across infrastructure
* Isolate risky or experimental tools

---

**Example Deployment Setup:**
Server Purpose Port `tools-search` Web search APIs 8000 `tools-imagegen` Stable Diffusion image generator 8001 `tools-voice` ElevenLabs voice synth server 8002
Each one runs a separate OpenAPI FastAPI instance!

---

**How Open WebUI handles this:**

* You connect each OpenAPI server independently.
* All tools are merged into the "tools available" list automatically.
* User sees tools unified at chat runtime.

✅ **No extra coding needed.** Just plug and play.

---

## 🔐 Part 8: Authentication (JWT, Bearer Tokens)

Open WebUI tools and chat completions require secure authorization:
Use Case Token Type Notes API endpoints Bearer Token (API Key) Generated via WebUI settings Custom tool server auth JWT preferred Validate via middleware

---

**🔑 How to Add Bearer Auth to Your Own OpenAPI Server:**
If you are writing a server with FastAPI:

```python
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
security = HTTPBearer()
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != "YOUR_SECRET_API_KEY":
        raise HTTPException(status_code=403, detail="Unauthorized")
```

Apply to endpoints:

```python
@app.get("/protected-endpoint")
async def protected_route(credentials: HTTPAuthorizationCredentials = Depends(verify_token)):
    return {"message": "Welcome Authorized User"}
```

✅ Now only authorized Open WebUI requests will reach your server.

---

**🧩 How to Validate JWT in Tools (Optional Advanced Security):**
If your tools expect user-specific permissions:

```python
import jwt
def decode_jwt(token: str):
    try:
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")
```

✅ This is good when your server shares login states or enforces per-user tool access.

---

## 🌎 Part 9: Deploying Production-Ready OpenAPI Tool Servers

When you’re ready to **move beyond localhost**, follow this checklist:

### 🧹 Server Hardening Checklist

* ✅ **Enable HTTPS** (Let's Encrypt via Traefik, nginx proxy, or native certs)
* ✅ **Restrict Origins** (`allow_origins=["https://yourdomain.com"]`)
* ✅ **Use Bearer Tokens** everywhere
* ✅ **Resource Limits** (timeout limits, memory constraints)
* ✅ **Observability** (enable logging, Sentry, tracing)
* ✅ **Run behind Reverse Proxy** (Caddy, nginx, Traefik)
* ✅ **Auto-Scaling** (optional: docker swarm, Kubernetes)

---

### 🛡️ Example: FastAPI Server Secured Behind Nginx

`nginx.conf`:

```nginx
server {
    listen 443 ssl;
    server_name yourserver.com;
    ssl_certificate /etc/letsencrypt/live/yourserver.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourserver.com/privkey.pem;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

✅ Serve OpenAPI securely without exposing your app's internals directly!

---

## 📑 Part 10: Templates for Your Own OpenAPI Servers

Want to build a tool server FAST? Use this base:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In prod, lock to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Tool definition
class ReverseInput(BaseModel):
    text: str
@app.post("/reverse")
async def reverse(input: ReverseInput):
    return {"reversed_text": input.text[::-1]}
```

Then:

```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```

Boom: you now have a **custom tool server** ready for [[sin/Initialization/Docs/Open WebUI Docs/Open WebUI tools|Open WebUI tools]]. 🚀