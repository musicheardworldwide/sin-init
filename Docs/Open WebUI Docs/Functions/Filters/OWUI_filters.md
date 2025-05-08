# Open WebUI Filter Functions: Comprehensive Technical Guide

## Core Concepts

Filter [[Functions]] are middleware components that transform data in [[sin/1. Initialization/Docs/Open WebUI Docs/Open WebUI tools|Open WebUI tools]]'s processing pipeline. They operate at two critical points:

[[tools-export-1745623456262.json]]. **Inlet Function**: Modifies user inputs before reaching the [[sin/1. Initialization/Docs/Datasets/8. Datasets]]
[[02-05-2025]]. **Outlet Function**: Processes model outputs before displaying to users

## Structural Anatomy

```python
from pydantic import BaseModel
from typing import Optional

class Filter:
    # Configuration parameters (optional)
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()

    def inlet(self, body: dict) -> dict:
        """Process input before LLM receives it"""
        return body

    def outlet(self, body: dict) -> None:
        """Process output before user sees it"""
        pass
```

## Component Deep Dive

### 1. Valves Configuration

The `Valves` class enables runtime configuration of filter behavior:

```python
class Valves(BaseModel):
    enable_uppercase: bool = True
    max_length: int = 1000
    allowed_patterns: list[str] = [r'\w+', r'\d+']
```

### 2. Inlet Function (Input Processing)

**Parameters**:
- `body`: Dict containing chat completion request (messages, model config, metadata)
- `__user__`: Optional user [[sin/1. Initialization/Docs/Prompting Guides/context]] dictionary

**Advanced Example: [[sin/1. Initialization/Docs/Prompting Guides/context]] Injection**

```python
def inlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
    # Add system message with dynamic context
    context = {
        "role": "system",
        "content": (
            f"You are assisting {__user__.get('name', 'a user')} with "
            f"technical support. Current time: {datetime.now().isoformat()}\n"
            "Provide concise, accurate answers with code examples when applicable."
        )
    }
    
    # Preserve existing system messages if present
    if not any(m.get('role') == 'system' for m in body.get('messages', [])):
        body.setdefault('messages', []).insert(0, context)
    
    # Sanitize input
    for message in body['messages']:
        if message['role'] == 'user':
            message['content'] = self._sanitize_input(message['content'])
    
    return body

def _sanitize_input(self, text: str) -> str:
    """Remove special characters and normalize whitespace"""
    import re
    text = re.sub(r'[^\w\s.,!?\-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text
```

### 3. Outlet Function (Output Processing)

**Advanced Example: Structured [[sin/1. Initialization/Docs/Prompting Guides/output]] Formatting**

```python
def outlet(self, body: dict, __user__: Optional[dict] = None) -> dict:
    for message in body['messages']:
        if message['role'] == 'assistant':
            content = message['content']
            
            # Apply markdown formatting
            if self.valves.enable_markdown:
                content = self._format_markdown(content)
            
            # Truncate if exceeding length limit
            if len(content) > self.valves.max_length:
                content = content[:self.valves.max_length] + "... [truncated]"
            
            message['content'] = content
    
    return body

def _format_markdown(self, text: str) -> str:
    """Convert plaintext to structured markdown"""
    import re
    
    # Format code blocks
    text = re.sub(r'```(\w+)?\n(.*?)\n```', 
                 r'```\1\n\2\n```', 
                 text, flags=re.DOTALL)
    
    # Format bullet points
    text = re.sub(r'^\s*[\-+*]\s+', '- ', text, flags=re.MULTILINE)
    
    return text
```

## Practical Implementation Examples

### Example 1: API Response Redaction

```python
class SensitiveDataFilter(Filter):
    class Valves(BaseModel):
        redaction_patterns: list[str] = [
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit cards
            r'\b\d{3}[- ]?\d{2}[- ]?\d{4}\b',  # SSNs
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Emails
        ]

    def outlet(self, body: dict) -> dict:
        import re
        for pattern in self.valves.redaction_patterns:
            for message in body['messages']:
                message['content'] = re.sub(
                    pattern, 
                    '[REDACTED]', 
                    message['content']
                )
        return body
```

### Example 2: Dynamic Context Injection

```python
class ContextAwareFilter(Filter):
    class Valves(BaseModel):
        user_role: str = "developer"
        knowledge_domain: str = "Python programming"
        response_style: str = "technical"

    def inlet(self, body: dict) -> dict:
        context = {
            "role": "system",
            "content": (
                f"You are assisting a {self.valves.user_role} with "
                f"{self.valves.knowledge_domain}. Respond in a "
                f"{self.valves.response_style} style. Provide accurate "
                "information with references when possible."
            )
        }
        body['messages'].insert(0, context)
        return body
```

### Example 3: Output Validation & Correction

```python
class FactCheckerFilter(Filter):
    class Valves(BaseModel):
        enable_fact_checking: bool = True
        minimum_confidence: float = 0.7

    def outlet(self, body: dict) -> dict:
        if not self.valves.enable_fact_checking:
            return body
            
        from fact_checker import verify_claims  # Hypothetical library
        
        for message in body['messages']:
            if message['role'] == 'assistant':
                claims = extract_claims(message['content'])
                corrections = []
                
                for claim in claims:
                    result = verify_claims(claim['text'])
                    if result.confidence < self.valves.minimum_confidence:
                        corrections.append(
                            f"\n\n[Correction: {result.corrected_text}]"
                        )
                
                if corrections:
                    message['content'] += "\n\n---\n" + "\n".join(corrections)
        
        return body
```

## Performance Considerations

[[tools-export-1745623456262.json]]. **Inlet Optimization**:
   - Process only the latest user message when possible
   - Use compiled regex patterns for repeated operations
   - Cache expensive operations (e.g., API calls)

[[02-05-2025]]. **Outlet Optimization**:
   - Limit processing to assistant responses
   - Implement early termination for long outputs
   - Use streaming modifications for large responses

## Debugging Techniques

```python
class DebugFilter(Filter):
    def inlet(self, body: dict) -> dict:
        import logging
        logging.debug(f"Raw input: {body}")
        processed = self._process_body(body)
        logging.debug(f"Processed input: {processed}")
        return processed

    def outlet(self, body: dict) -> dict:
        import logging
        logging.debug(f"Raw output: {body}")
        if any(m['role'] == 'assistant' for m in body['messages']):
            logging.info("Assistant response detected")
        return body
```

## Best Practices

[[tools-export-1745623456262.json]]. **Idempotency**: Ensure repeated processing yields same results
[[02-05-2025]]. **Reversibility**: Maintain original meaning through transformations
[[tools-export-1745623456262.json]]. **Performance**: Profile filters with realistic payloads
[[tools-export-1745623456262.json]]. **Configuration**: Expose essential parameters through Valves
[[02-05-2025]]. **Error Handling**: Gracefully handle malformed inputs

## Integration Patterns

```python
# Chaining multiple filters
from openwebui import FilterPipeline

pipeline = FilterPipeline([
    InputSanitizerFilter(),
    ContextEnhancerFilter(),
    OutputFormatterFilter()
])

# Applying to specific routes
@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    processed_data = pipeline.inlet(data)
    response = await llm_call(processed_data)
    return pipeline.outlet(response)
```