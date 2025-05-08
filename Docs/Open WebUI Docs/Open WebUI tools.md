---
aliases:
  - Open WebUI
  - UI
---
# Open WebUI Tools: Technical Implementation Guide

## Core Architecture

[[Tools]] are Python scripts that enable LLMs to perform external actions through function calling. They consist of:

[[tools-export-1745623456262.json]]. **Metadata**: Defined in the module docstring
[[02-05-2025]]. **[[Tools]] Class**: Contains the executable methods
[[tools-export-1745623456262.json]]. **Valves/UserValves**: Configuration parameters (admin/user configurable)

## Implementation Template

```python
"""
title: [Tool Name]
author: [Author Name]
author_url: [Author URL]
git_url: [Repository URL]
description: [Tool description]
required_open_webui_version: [Minimum Version]
requirements: [Dependencies]
version: [SemVer]
license: [License Type]
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import httpx

class Tools:
    class Valves(BaseModel):
        """Admin-configurable parameters"""
        api_endpoint: str = Field(
            default="https://api.example.com/v1",
            description="Base API endpoint URL"
        )
        rate_limit: int = Field(
            default=10,
            description="Max requests per minute"
        )

    class UserValves(BaseModel):
        """User-configurable parameters"""
        enable_feature: bool = Field(
            default=False,
            description="Toggle experimental features"
        )
        detail_level: int = Field(
            default=1,
            description="Output detail level (1-3)",
            ge=1, le=3
        )

    def __init__(self):
        self.valves = self.Valves()
        self.user_valves = self.UserValves()
        self.client = httpx.AsyncClient(timeout=30)
```

## Advanced Implementation Examples

### Example 1: Real-Time Data Fetcher

```python
async def stock_data(
    self,
    symbol: str,
    timeframe: str = "1d",
    __event_emitter__=None,
    __user__=Optional[Dict]
) -> Dict[str, Any]:
    """
    Fetch real-time stock market data
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL)
        timeframe: Data interval (1d, 1wk, 1mo)
    Returns:
        Dictionary containing OHLCV data
    """
    if __event_emitter__:
        await __event_emitter__({
            "type": "status",
            "data": {"description": f"Fetching {symbol} data", "done": False}
        })

    try:
        response = await self.client.get(
            f"{self.valves.api_endpoint}/market-data",
            params={
                "symbol": symbol,
                "interval": timeframe,
                "detail": self.user_valves.detail_level
            },
            headers={"Authorization": f"Bearer {__user__.get('api_key', '')}"}
        )
        data = response.json()

        if __event_emitter__:
            await __event_emitter__({
                "type": "message",
                "data": {"content": f"Found {len(data['points'])} data points"}
            })

        return {
            "symbol": symbol,
            "data": data,
            "metadata": {
                "timeframe": timeframe,
                "source": self.valves.api_endpoint
            }
        }

    except Exception as e:
        if __event_emitter__:
            await __event_emitter__({
                "type": "status",
                "data": {"description": f"Error: {str(e)}", "done": True}
            })
        raise
```

### Example 2: Multi-Step Research Tool

```python
async def research_assistant(
    self,
    query: str,
    max_sources: int = 3,
    __event_emitter__=None,
    __files__=Optional[List]
) -> Dict[str, Any]:
    """
    Conduct comprehensive research using multiple sources
    
    Args:
        query: Research question
        max_sources: Maximum sources to consult
    Returns:
        Structured research findings
    """
    # Phase 1: Source identification
    await __event_emitter__({
        "type": "status",
        "data": {"description": "Identifying relevant sources", "done": False}
    })
    
    sources = await self._identify_sources(query, max_sources)
    
    # Phase 2: Parallel data collection
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for source in sources:
            tasks.append(tg.create_task(
                self._gather_data(source, __event_emitter__)
            ))
    
    # Phase 3: Analysis and synthesis
    await __event_emitter__({
        "type": "status",
        "data": {"description": "Analyzing findings", "done": False}
    })
    
    findings = await self._analyze_results(
        [task.result() for task in tasks],
        __files__
    )
    
    return {
        "query": query,
        "sources": [s['url'] for s in sources],
        "findings": findings,
        "recommendations": await self._generate_recommendations(findings)
    }
```

### Example 3: File Processor with Metadata Extraction

```python
async def process_document(
    self,
    file_path: str,
    extract_entities: bool = True,
    __event_emitter__=None,
    __metadata__=Optional[Dict]
) -> Dict[str, Any]:
    """
    Process and analyze document files
    
    Args:
        file_path: Path to document file
        extract_entities: Whether to identify named entities
    Returns:
        Document analysis results
    """
    from unstructured.partition.auto import partition
    from unstructured.staging.base import convert_to_dict
    
    try:
        # Document parsing
        await __event_emitter__({
            "type": "status",
            "data": {"description": "Parsing document", "done": False}
        })
        
        elements = partition(filename=file_path)
        doc_data = convert_to_dict(elements)
        
        # Metadata enrichment
        if __metadata__:
            doc_data['conversation_id'] = __metadata__.get('conversation_id')
            doc_data['user_id'] = __metadata__.get('user_id')
        
        # Entity extraction
        if extract_entities:
            await __event_emitter__({
                "type": "status",
                "data": {"description": "Extracting entities", "done": False}
            })
            doc_data['entities'] = await self._extract_entities(elements)
        
        return doc_data
        
    except Exception as e:
        await __event_emitter__({
            "type": "status",
            "data": {"description": f"Processing failed: {str(e)}", "done": True}
        })
        raise
```

## Event Emission Patterns

### Real-Time Progress Updates

```python
async def long_running_task(self, __event_emitter__=None):
    stages = [
        ("Initializing", 0.1),
        ("Processing data", 0.4),
        ("Validating results", 0.3),
        ("Finalizing", 0.2)
    ]
    
    for description, duration in stages:
        await __event_emitter__({
            "type": "status",
            "data": {
                "description": description,
                "progress": int(duration * 100),
                "done": False
            }
        })
        await asyncio.sleep(duration * 10)  # Simulate work
        
    await __event_emitter__({
        "type": "status",
        "data": {"description": "Completed", "done": True}
    })
```

### Interactive Confirmation Flow

```python
async def sensitive_operation(self, __event_call__=None):
    confirmation = await __event_call__({
        "type": "confirm",
        "data": {
            "title": "Critical Operation",
            "message": "This will modify production data. Continue?",
            "confirm_text": "Proceed",
            "cancel_text": "Abort"
        }
    })
    
    if not confirmation:
        return {"status": "operation_cancelled"}
    
    # Proceed with operation
```

## Best Practices

[[tools-export-1745623456262.json]]. **Type Hinting**: Always use Python type hints for all parameters and return values
[[02-05-2025]]. **Error Handling**: Implement comprehensive error handling with user feedback
[[tools-export-1745623456262.json]]. **Resource Management**: Use [[sin/1. Initialization/Docs/Prompting Guides/context]] managers for external connections
[[tools-export-1745623456262.json]]. **Documentation**: Provide detailed docstrings with examples
[[02-05-2025]]. **Configuration**: Expose essential parameters through Valves/UserValves
6. **Performance**: Implement asynchronous operations for I/O-bound tasks
7. **Security**: Never hardcode sensitive credentials - use Valves instead

## Security Considerations

```python
class SecureAPITool:
    class Valves(BaseModel):
        api_key: str = Field(
            default="",
            description="Service API key",
            json_schema_extra={"secret": True}  # Marks as sensitive
        )
        allowed_domains: List[str] = Field(
            default=["api.trusted.com"],
            description="Whitelisted API endpoints"
        )

    async def safe_api_call(self, endpoint: str):
        if not any(endpoint.startswith(d) for d in self.valves.allowed_domains):
            raise ValueError("Unauthorized API endpoint")
        
        # Proceed with API call
```