# Open WebUI Pipe Functions: Advanced Implementation Guide

## Core Architecture

Pipe [[sin/Initialization/Docs/Open WebUI Docs/Functions/Functions]] enable custom model integration in [[sin/Initialization/Docs/Open WebUI Docs/Open WebUI tools|Open WebUI tools]] through a plugin system with three key components:

[[tools-export-1745623456262.json]]. **Valves**: Runtime-configurable parameters (persistent settings)
[[02-05-2025]]. **pipes()**: Model registration and discovery
[[tools-export-1745623456262.json]]. **pipe()**: Core processing logic

## Structural Template

```python
"""
title: [Your Pipe Title]
author: [Your Name]
description: [Brief functionality description]
version: [SemVer]
required_open_webui_version: [Minimum Version]
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union, AsyncGenerator
import httpx
import json

class Pipe:
    class Valves(BaseModel):
        """Runtime-configurable parameters"""
        api_base: str = Field(
            default="https://api.example.com/v1",
            description="Base URL for API endpoints"
        )
        api_key: str = Field(
            default="",
            description="Service API key",
            json_schema_extra={"secret": True}
        )
        timeout: int = Field(
            default=30,
            description="Request timeout in seconds",
            ge=5, le=120
        )

    def __init__(self):
        """Initialize pipe with configured valves"""
        self.valves = self.Valves()
        self.client = httpx.AsyncClient(timeout=self.valves.timeout)

    async def pipes(self) -> List[Dict[str, str]]:
        """Register available models"""
        return [
            {"id": "model-1", "name": "Custom Model 1"},
            {"id": "model-2", "name": "Specialized Model 2"}
        ]

    async def pipe(
        self,
        body: Dict[str, Any],
        __user__: Optional[Dict] = None,
        __request__: Optional[Any] = None
    ) -> Union[Dict, AsyncGenerator]:
        """Process incoming requests"""
        pass
```

## Implementation Examples

### Example 1: Advanced OpenAI Proxy

```python
class OpenAIPipe(Pipe):
    class Valves(BaseModel):
        organization: str = Field(default="", description="OpenAI Org ID")
        rate_limit: int = Field(default=5, description="Max requests per minute")
        fallback_model: str = Field(default="gpt-3.5-turbo")

    async def pipes(self) -> List[Dict[str, str]]:
        """Dynamic model discovery"""
        if not self.valves.api_key:
            return [{"id": "error", "name": "API key required"}]

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.valves.api_base}/models",
                    headers={
                        "Authorization": f"Bearer {self.valves.api_key}",
                        "OpenAI-Organization": self.valves.organization
                    },
                    timeout=10
                )
                models = resp.json()
                return [
                    {
                        "id": model["id"],
                        "name": f"OpenAI/{model['id']}",
                        "meta": {
                            "capabilities": model.get("capabilities", []),
                            "deprecated": model.get("deprecated", False)
                        }
                    }
                    for model in models["data"]
                    if model["id"].startswith("gpt")
                ]
            except Exception as e:
                return [{"id": "fallback", "name": self.valves.fallback_model}]

    async def pipe(self, body: Dict, **kwargs) -> Union[Dict, AsyncGenerator]:
        """Process OpenAI-compatible requests"""
        headers = {
            "Authorization": f"Bearer {self.valves.api_key}",
            "OpenAI-Organization": self.valves.organization,
            "Content-Type": "application/json"
        }

        # Model selection fallback
        requested_model = body.get("model", "")
        if not any(m["id"] == requested_model for m in await self.pipes()):
            body["model"] = self.valves.fallback_model

        try:
            async with self.client.stream(
                "POST",
                f"{self.valves.api_base}/chat/completions",
                json=body,
                headers=headers
            ) as response:
                if body.get("stream", False):
                    async for chunk in response.aiter_lines():
                        yield json.loads(chunk[6:])  # Skip "data: " prefix
                else:
                    return await response.json()
        except httpx.RequestError as e:
            return {
                "error": {
                    "message": str(e),
                    "type": "api_error",
                    "code": 503
                }
            }
```

### Example 2: Hybrid Local/Cloud Model Router

```python
class HybridRouterPipe(Pipe):
    class Valves(BaseModel):
        local_endpoint: str = Field(
            default="http://localhost:5000",
            description="Local inference server"
        )
        cloud_fallback: bool = Field(
            default=True,
            description="Use cloud when local fails"
        )
        cost_tracking: bool = Field(
            default=False,
            description="Enable usage cost tracking"
        )

    async def pipes(self):
        return [
            {"id": "hybrid-smart", "name": "Smart Router"},
            {"id": "hybrid-local", "name": "Local Only"},
            {"id": "hybrid-cloud", "name": "Cloud Only"}
        ]

    async def pipe(self, body: Dict, __user__: Dict = None):
        strategy = body["model"].split("-")[-1]
        payload = {
            "messages": body["messages"],
            "temperature": body.get("temperature", 0.7),
            "max_tokens": body.get("max_tokens", 1000)
        }

        # Routing logic
        if strategy == "local":
            return await self._call_local(payload)
        elif strategy == "cloud":
            return await self._call_cloud(payload)
        else:  # smart routing
            try:
                result = await self._call_local(payload)
                if self.valves.cost_tracking:
                    self._track_usage(__user__["id"], "local")
                return result
            except Exception:
                if self.valves.cloud_fallback:
                    result = await self._call_cloud(payload)
                    if self.valves.cost_tracking:
                        self._track_usage(__user__["id"], "cloud")
                    return result
                raise

    async def _call_local(self, payload: Dict) -> Dict:
        async with self.client.post(
            f"{self.valves.local_endpoint}/generate",
            json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def _call_cloud(self, payload: Dict) -> Dict:
        # Implementation similar to OpenAI example
        pass

    def _track_usage(self, user_id: str, provider: str):
        # Implement usage tracking logic
        pass
```

### Example 3: Advanced RAG Pipeline

```python
class RAGPipe(Pipe):
    class Valves(BaseModel):
        embedding_model: str = Field(default="text-embedding-3-small")
        chunk_size: int = Field(default=512, description="Token chunk size")
        top_k: int = Field(default=3, description="Retrieval count")
        hybrid_search: bool = Field(default=True)

    async def pipe(self, body: Dict, __request__: Any = None):
        from open_webui.rag import VectorStore  # Hypothetical internal module
        
        # 1. Query Understanding
        query = body["messages"][-1]["content"]
        query_embedding = await self._get_embedding(query)
        
        # 2. Context Retrieval
        store = VectorStore.from_request(__request__)
        if self.valves.hybrid_search:
            docs = await store.hybrid_search(
                query=query,
                embedding=query_embedding,
                k=self.valves.top_k
            )
        else:
            docs = await store.semantic_search(
                embedding=query_embedding,
                k=self.valves.top_k
            )
        
        # 3. Prompt Augmentation
        context = "\n\n".join(doc.content for doc in docs)
        augmented_prompt = f"""Use the following context:
{context}

Answer this question: {query}"""
        
        # 4. LLM Generation
        llm_body = {
            **body,
            "messages": [
                *body["messages"][:-1],
                {"role": "user", "content": augmented_prompt}
            ]
        }
        
        # Forward to configured LLM
        return await generate_chat_completion(__request__, llm_body)

    async def _get_embedding(self, text: str) -> List[float]:
        """Generate text embeddings"""
        async with self.client.post(
            f"{self.valves.api_base}/embeddings",
            json={"input": text, "model": self.valves.embedding_model},
            headers={"Authorization": f"Bearer {self.valves.api_key}"}
        ) as response:
            data = await response.json()
            return data["data"][0]["embedding"]
```

## Advanced Patterns

### 1. Multi-Modal Processing

```python
class MultiModalPipe(Pipe):
    class Valves(BaseModel):
        image_model: str = Field(default="clip-vit-base-patch32")
        text_model: str = Field(default="gpt-4-vision-preview")

    async def pipe(self, body: Dict):
        # Extract multi-modal inputs
        text_inputs = [m["content"] for m in body["messages"] if isinstance(m["content"], str)]
        image_inputs = [m["images"] for m in body["messages"] if "images" in m]
        
        # Parallel processing
        async with asyncio.TaskGroup() as tg:
            text_task = tg.create_task(self._process_text(text_inputs))
            image_task = tg.create_task(self._process_images(image_inputs))
        
        # Fusion
        combined = f"TEXT:\n{text_task.result()}\n\nIMAGES:\n{image_task.result()}"
        return {"role": "assistant", "content": combined}
```

### 2. Stateful Conversation Management

```python
class StatefulPipe(Pipe):
    class Valves(BaseModel):
        memory_window: int = Field(default=5, description="Turn history to retain")
        persona: str = Field(default="helpful_assistant")

    def __init__(self):
        super().__init__()
        self.conversations = {}  # {conversation_id: history}

    async def pipe(self, body: Dict, __user__: Dict):
        conv_id = body.get("conversation_id", "default")
        
        # Initialize or retrieve conversation state
        if conv_id not in self.conversations:
            self.conversations[conv_id] = {
                "history": [],
                "persona": self.valves.persona
            }
        
        # Update history
        self.conversations[conv_id]["history"].extend(body["messages"])
        if len(self.conversations[conv_id]["history"]) > self.valves.memory_window:
            self.conversations[conv_id]["history"] = self.conversations[conv_id]["history"][-self.valves.memory_window:]
        
        # Generate response using full context
        response = await self._generate_response(
            self.conversations[conv_id]["history"],
            self.conversations[conv_id]["persona"]
        )
        
        # Update history with response
        self.conversations[conv_id]["history"].append({
            "role": "assistant",
            "content": response
        })
        
        return response
```

## Performance Optimization

[[tools-export-1745623456262.json]]. **Connection Pooling**:
```python
def __init__(self):
    self.valves = self.Valves()
    transport = httpx.AsyncHTTPTransport(
        retries=3,
        max_connections=100,
        max_keepalive_connections=20
    )
    self.client = httpx.AsyncClient(
        transport=transport,
        timeout=self.valves.timeout
    )
```

[[02-05-2025]]. **Response Streaming**:
```python
async def pipe(self, body: Dict) -> AsyncGenerator:
    async with self.client.stream("POST", "...", json=body) as response:
        async for chunk in response.aiter_bytes():
            if chunk:
                yield json.loads(chunk)
```

[[tools-export-1745623456262.json]]. **Caching**:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
async def _get_embedding(self, text: str) -> List[float]:
    """Cache frequent embedding requests"""
    pass
```

## Security Considerations

[[tools-export-1745623456262.json]]. **Secret Management**:
```python
class Valves(BaseModel):
    api_key: str = Field(
        default="",
        description="Sensitive credentials",
        json_schema_extra={"secret": True}  # Marks field as sensitive
    )
```

[[02-05-2025]]. **Input Validation**:
```python
from pydantic import validator

class Valves(BaseModel):
    @validator('api_base')
    def validate_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Invalid URL scheme")
        return v.rstrip('/')
```

[[tools-export-1745623456262.json]]. **Rate Limiting**:
```python
from fastapi import HTTPException

async def pipe(self, body: Dict, __request__: Request):
    if self._is_rate_limited(__request__.client.host):
        raise HTTPException(429, "Rate limit exceeded")
    # Continue processing
```

## Monitoring & Observability

```python
class InstrumentedPipe(Pipe):
    async def pipe(self, body: Dict, **kwargs):
        start_time = time.time()
        try:
            # Process request
            result = await self._process(body)
            
            # Log success
            self._log_metrics(
                duration=time.time() - start_time,
                status="success",
                model=body.get("model")
            )
            return result
            
        except Exception as e:
            # Log failure
            self._log_metrics(
                duration=time.time() - start_time,
                status="failed",
                error=str(e)
            )
            raise

    def _log_metrics(self, **fields):
        # Integrate with monitoring system
        print(f"[METRIC] {json.dumps(fields)}")
```