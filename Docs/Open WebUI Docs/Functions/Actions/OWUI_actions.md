# Open WebUI Action Functions: Technical Implementation Guide

## Core Concept
Action [[Functions]] enable custom interactive buttons in [[sin/1. Initialization/Docs/Open WebUI Docs/Open WebUI tools|Open WebUI tools]]'s message toolbar, allowing users to trigger specific operations on chat messages.

## Structural Template
```python
"""
title: [Your Action Name]
author: [Your Name]
author_url: [Your GitHub/Website]
funding_url: [Optional Sponsorship Link]
version: [Semantic Version]
required_open_webui_version: [Minimum Compatible Version]
"""

from pydantic import BaseModel, Field
from typing import Optional, Union, Generator, Iterator
import os
import requests
import asyncio

class Action:
    class Valves(BaseModel):
        # Configuration parameters
        pass

    def __init__(self):
        self.valves = self.Valves()

    async def action(
        self,
        body: dict,
        __user__=None,
        __event_emitter__=None,
        __event_call__=None,
    ) -> Optional[dict]:
        """Core action logic"""
        pass
```

## Key Components

### 1. Valves Configuration
```python
class Valves(BaseModel):
    api_key: str = Field(default="", description="Third-party API key")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    enable_logging: bool = Field(default=True, description="Enable debug logging")
```

### 2. Action Function Parameters
- `body`: Contains complete message [[sin/1. Initialization/Docs/Prompting Guides/context]] including:
  ```python
  {
      "content": "Original message text",
      "metadata": {...},
      "message_id": "unique-id",
      "timestamp": "ISO-8601"
  }
  ```
- `__user__`: Current user [[sin/1. Initialization/Docs/Prompting Guides/context]] (name, preferences, etc.)
- `__event_emitter__`: Callback for real-[[sin/1. Initialization/Tools/MCP Server Tools/Time/time]] [[sin/1. Initialization/Docs/Open WebUI Docs/Open WebUI tools|Open WebUI tools]] updates
- `__event_call__`: Method to request user input

## Implementation Examples

### Example 1: Message Enhancement Action
```python
async def action(self, body: dict, __user__=None, __event_emitter__=None, __event_call__=None):
    # Request user input for enhancement type
    enhancement = await __event_call__({
        "type": "select",
        "data": {
            "title": "Enhance Message",
            "options": [
                {"label": "Formal Tone", "value": "formal"},
                {"label": "Simplify Language", "value": "simple"},
                {"label": "Add Examples", "value": "examples"}
            ],
            "default": "formal"
        }
    })

    # Show processing status
    await __event_emitter__({
        "type": "status",
        "data": {"description": "Enhancing message...", "done": False}
    })

    # Process enhancement (mock implementation)
    enhanced_text = await self._enhance_message(body['content'], enhancement)

    # Return enhanced message
    return {
        "content": enhanced_text,
        "metadata": {
            "original_message": body['content'],
            "enhancement_type": enhancement
        }
    }

async def _enhance_message(self, text: str, style: str) -> str:
    """Apply text transformations based on enhancement type"""
    styles = {
        "formal": f"Formal version: {text.capitalize()}",
        "simple": f"Simplified: {text.lower()}",
        "examples": f"{text}\n\nExamples:\n- Example 1\n- Example 2"
    }
    return styles.get(style, text)
```

### Example 2: Data Visualization Action
```python
async def action(self, body: dict, __event_emitter__=None, __event_call__=None):
    # Extract potential data structures from message
    data = self._extract_structured_data(body['content'])
    
    if not data:
        return {"error": "No structured data found"}

    # Let user select visualization type
    viz_type = await __event_call__({
        "type": "select",
        "data": {
            "title": "Visualization Type",
            "options": [
                {"label": "Bar Chart", "value": "bar"},
                {"label": "Line Graph", "value": "line"},
                {"label": "Pie Chart", "value": "pie"}
            ]
        }
    })

    # Generate visualization
    chart_url = await self._generate_chart(data, viz_type)

    # Return HTML embed
    return {
        "content": f"<img src='{chart_url}' alt='Generated chart'>",
        "metadata": {
            "chart_type": viz_type,
            "data_points": len(data)
        }
    }

def _extract_structured_data(self, text: str) -> list:
    """Extract potential data points from message text"""
    import re
    # Simple pattern matching for demonstration
    return re.findall(r'\b\d+\b', text)

async def _generate_chart(self, data: list, chart_type: str) -> str:
    """Generate chart using visualization service"""
    # In production, replace with actual API call
    return f"https://quickchart.io/chart?c={{type:'{chart_type}',data:{{labels:{data},datasets:[{{data:{data}}]}}}}"
```

### Example 3: API Integration Action
```python
class Valves(BaseModel):
    weather_api_key: str = Field(..., description="OpenWeatherMap API key")
    default_location: str = Field("New York", description="Fallback location")

async def action(self, body: dict, __event_emitter__=None, __event_call__=None):
    # Extract location from message or request input
    location = self._extract_location(body['content'])
    
    if not location:
        response = await __event_call__({
            "type": "input",
            "data": {
                "title": "Weather Check",
                "message": "Enter location for weather:",
                "placeholder": self.valves.default_location
            }
        })
        location = response or self.valves.default_location

    # Get weather data
    weather = await self._fetch_weather(location)
    
    # Format response
    return {
        "content": (
            f"Weather in {location}:\n"
            f"Temperature: {weather['temp']}°C\n"
            f"Conditions: {weather['description']}\n"
            f"Humidity: {weather['humidity']}%"
        ),
        "metadata": {
            "location": location,
            "source": "OpenWeatherMap"
        }
    }

async def _fetch_weather(self, location: str) -> dict:
    """Fetch weather data from API"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={self.valves.weather_api_key}&units=metric"
    async with requests.AsyncClient() as client:
        response = await client.get(url, timeout=self.valves.timeout)
        data = response.json()
        return {
            "temp": data['main']['temp'],
            "description": data['weather'][0]['description'],
            "humidity": data['main']['humidity']
        }
```

## Advanced Patterns

### 1. Multi-step Workflow
```python
async def action(self, body: dict, __event_emitter__=None, __event_call__=None):
    # Step 1: Confirm action
    confirm = await __event_call__({
        "type": "confirm",
        "data": {
            "title": "Data Analysis",
            "message": "This will process the message for insights. Continue?"
        }
    })
    if not confirm:
        return {"status": "cancelled"}

    # Step 2: Select analysis type
    analysis_type = await __event_call__({
        "type": "select",
        "data": {
            "options": [
                {"label": "Sentiment Analysis", "value": "sentiment"},
                {"label": "Keyword Extraction", "value": "keywords"},
                {"label": "Summary Generation", "value": "summary"}
            ]
        }
    })

    # Step 3: Process analysis
    result = await self._analyze_content(body['content'], analysis_type)
    
    return {
        "content": result,
        "metadata": {"analysis_type": analysis_type}
    }
```

### 2. Real-time Progress Updates
```python
async def action(self, body: dict, __event_emitter__=None, __event_call__=None):
    await __event_emitter__({
        "type": "status",
        "data": {"description": "Starting process...", "done": 0}
    })
    
    for i in range(1, 6):
        await asyncio.sleep(0.5)  # Simulate work
        await __event_emitter__({
            "type": "status",
            "data": {"description": f"Processing step {i}/5", "done": i/5}
        })
    
    await __event_emitter__({
        "type": "status",
        "data": {"description": "Process complete", "done": 1}
    })
    
    return {"content": "Operation completed successfully"}
```

## Best Practices

[[tools-export-1745623456262.json]]. **User Feedback**: Always provide visual feedback during long operations
[[02-05-2025]]. **Error Handling**: Gracefully handle API failures and invalid inputs
[[tools-export-1745623456262.json]]. **Validation**: Sanitize all user-provided data before processing
[[tools-export-1745623456262.json]]. **Performance**: Optimize for quick response times (<[[02-05-2025]] seconds)
[[02-05-2025]]. **Idempotency**: Ensure repeat executions produce consistent results

## Debugging Techniques

```python
async def action(self, body: dict, **kwargs):
    # Log initial state
    print(f"Action triggered with: {body}")
    
    try:
        # Your action logic
        result = await self._process_action(body)
        
        # Log successful completion
        print(f"Action completed: {result}")
        return result
        
    except Exception as e:
        # Log errors
        print(f"Action failed: {str(e)}")
        return {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
```