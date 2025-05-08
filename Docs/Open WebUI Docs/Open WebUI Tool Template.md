Here's the breakdown of your Python script in Markdown format:

# Open WebUI Advanced Tool Documentation

## Metadata
```markdown
title: OpenWebUI Advanced Tool
author: Wes Caldwell
email: musicheardworldwide@gmail.com
author_url: https://github.com/musicheardworldwide
version: 1.0.0
license: MIT
description: A structured Open WebUI tool with advanced features, logging, and error handling.
requirements:
```

## Imports
```python
import json
import logging
import traceback
from typing import Optional, Callable, Any, Dict
from pydantic import BaseModel, Field
from fastapi import Request
from open_webui.utils.chat import generate_chat_completion
from open_webui.utils.misc import get_last_user_message
from open_webui.models.users import User
```

## Logging Configuration
```python
# Configure Logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

## Error Handling
```python
def handle_error(exception: Exception, function_name: str, inputs: dict) -> dict:
    """
    Handles errors and returns a structured response for OpenWebUI.
    
    Args:
        exception (Exception): The caught exception.
        function_name (str): The name of the function where the error occurred.
        inputs (dict): The original function inputs for debugging.
    
    Returns:
        dict: A structured error message to pass to OpenWebUI.
    """
    error_message = str(exception)
    stack_trace = traceback.format_exc()
    logger.error(f"Error in {function_name}: {error_message}")
    logger.debug(f"Stack Trace:\n{stack_trace}")

    return {
        "error": True,
        "function": function_name,
        "message": error_message,
        "stack_trace": stack_trace,
        "inputs": inputs,
        "suggestion": "Check input values and ensure the correct API configurations.",
    }
```

## Tool Definition
```python
class Tools:
    """
    OpenWebUI Tool with proper request handling, event emissions, and structured processing.
    """
```

## Configuration Model
```python
    class Config(BaseModel):
        API_ENDPOINT: str = Field(
            default="https://api.example.com/search",
            description="API endpoint for fetching external data",
        )
        API_KEY: str = Field(default="", description="API key for authentication")
        ENABLE_LOGGING: bool = Field(
            default=True, description="Enable or disable logging for debugging"
        )
```

## Initialization
```python
    def __init__(self):
        self.config = self.Config()
```

## Request Processing
```python
    async def process_request(
        self, query: str, __event_emitter__: Optional[Callable[[Any], Any]] = None
    ) -> Dict:
        """
        Processes an external API request.
        
        Args:
            query (str): The search query.
            __event_emitter__ (Callable): Emits events back to OpenWebUI.
        
        Returns:
            Dict: API response or an error message.
        """
        try:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Processing request...", "done": False},
                    }
                )

            # Simulated API request
            response = {
                "status": "success",
                "query": query,
                "results": ["Item 1", "Item 2"],
            }
            logger.info(f"API Response: {response}")

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Request complete.", "done": True},
                    }
                )

            return response

        except Exception as e:
            return handle_error(e, "process_request", {"query": query})
```

## Inlet Method
```python
    def inlet(self, body: Dict, __user__: Optional[Dict] = None) -> Dict:
        """
        Pre-processes the request before execution.
        
        Args:
            body (Dict): The request payload.
            __user__ (Optional[Dict]): User metadata.
        
        Returns:
            Dict: Modified request payload.
        """
        try:
            messages = body.get("messages", [])
            user_message = get_last_user_message(messages)

            logger.info(f"Inlet: Processing input -> {user_message}")
            body["processed_input"] = True
            return body

        except Exception as e:
            return handle_error(e, "inlet", body)
```

## Outlet Method
```python
    def outlet(self, body: Dict, __user__: Optional[Dict] = None) -> Dict:
        """
        Post-processes the response after execution.
        
        Args:
            body (Dict): The response payload.
            __user__ (Optional[Dict]): User metadata.
        
        Returns:
            Dict: Modified response payload.
        """
        try:
            logger.info(f"Outlet: Adjusting response data...")
            body["processed_output"] = True
            return body

        except Exception as e:
            return handle_error(e, "outlet", body)
```

## Action Method
```python
    async def action(
        self,
        body: Dict,
        __user__: Optional[Dict] = None,
        __event_emitter__: Optional[Callable] = None,
        __event_call__: Optional[Callable] = None,
    ) -> Dict:
        """
        Handles interactive actions.
        
        Args:
            body (Dict): Action request data.
            __user__ (Optional[Dict]): User metadata.
            __event_emitter__ (Callable): Emits events.
            __event_call__ (Callable): Calls interactive events.
        
        Returns:
            Dict: Action response.
        """
        try:
            if __event_call__:
                user_response = await __event_call__(
                    {
                        "type": "input",
                        "data": {
                            "title": "Confirm Action",
                            "message": "Proceed with the operation?",
                            "placeholder": "yes/no",
                        },
                    }
                )

                return {"confirmation": user_response}

            return {"error": "No event call provided."}

        except Exception as e:
            return handle_error(e, "action", body)
```

## Pipe Method
```python
    async def pipe(self, body: Dict, __user__: Dict, __request__: Request) -> Dict:
        """
        Processes requests with API integration.
        
        Args:
            body (Dict): The request payload.
            __user__ (Dict): User metadata.
            __request__ (Request): FastAPI request object.
        
        Returns:
            Dict: Processed response.
        """
        try:
            logger.info("Processing request in Pipe...")

            messages = body.get("messages", [])
            if not messages:
                return handle_error(ValueError("No input messages found"), "pipe", body)

            user_message = messages[-1].get("content", "")
            modified_query = f"Processed Query: {user_message}"

            response_data = await self.process_request(modified_query)

            body["messages"].append(
                {"role": "assistant", "content": json.dumps(response_data)}
            )
            return body

        except Exception as e:
            return handle_error(e, "pipe", body)
```

## Example Usage
```python
if __name__ == "__main__":
    tool = Tools()

    async def test_tool():
        response = await tool.process_request("Example query")
        print(json.dumps(response, indent=4))

    import asyncio

    asyncio.run(test_tool())
```

And now, all together:

```python
title: OpenWebUI Advanced Tool
author: Wes Caldwell
email: musicheardworldwide@gmail.com
author_url: https://github.com/musicheardworldwide
version: 1.0.0
license: MIT
description: A structured Open WebUI tool with advanced features, logging, and error handling.
requirements:


import json
import logging
import traceback
from typing import Optional, Callable, Any, Dict
from pydantic import BaseModel, Field
from fastapi import Request
from open_webui.utils.chat import generate_chat_completion
from open_webui.utils.misc import get_last_user_message
from open_webui.models.users import User

# Configure Logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)


# Centralized Error Handling Function
def handle_error(exception: Exception, function_name: str, inputs: dict) -> dict:
    """
    Handles errors and returns a structured response for OpenWebUI.

    Args:
        exception (Exception): The caught exception.
        function_name (str): The name of the function where the error occurred.
        inputs (dict): The original function inputs for debugging.

    Returns:
        dict: A structured error message to pass to OpenWebUI.
    """
    error_message = str(exception)
    stack_trace = traceback.format_exc()
    logger.error(f"Error in {function_name}: {error_message}")
    logger.debug(f"Stack Trace:\n{stack_trace}")

    return {
        "error": True,
        "function": function_name,
        "message": error_message,
        "stack_trace": stack_trace,
        "inputs": inputs,
        "suggestion": "Check input values and ensure the correct API configurations.",
    }


# Tool Definition
class Tools:
    """
    OpenWebUI Tool with proper request handling, event emissions, and structured processing.
    """

    class Config(BaseModel):
        API_ENDPOINT: str = Field(
            default="https://api.example.com/search",
            description="API endpoint for fetching external data",
        )
        API_KEY: str = Field(default="", description="API key for authentication")
        ENABLE_LOGGING: bool = Field(
            default=True, description="Enable or disable logging for debugging"
        )

    def __init__(self):
        self.config = self.Config()

    async def process_request(
        self, query: str, __event_emitter__: Optional[Callable[[Any], Any]] = None
    ) -> Dict:
        """
        Processes an external API request.

        Args:
            query (str): The search query.
            __event_emitter__ (Callable): Emits events back to OpenWebUI.

        Returns:
            Dict: API response or an error message.
        """
        try:
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Processing request...", "done": False},
                    }
                )

            # Simulated API request
            response = {
                "status": "success",
                "query": query,
                "results": ["Item 1", "Item 2"],
            }
            logger.info(f"API Response: {response}")

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Request complete.", "done": True},
                    }
                )

            return response

        except Exception as e:
            return handle_error(e, "process_request", {"query": query})

    def inlet(self, body: Dict, __user__: Optional[Dict] = None) -> Dict:
        """
        Pre-processes the request before execution.

        Args:
            body (Dict): The request payload.
            __user__ (Optional[Dict]): User metadata.

        Returns:
            Dict: Modified request payload.
        """
        try:
            messages = body.get("messages", [])
            user_message = get_last_user_message(messages)

            logger.info(f"Inlet: Processing input -> {user_message}")
            body["processed_input"] = True
            return body

        except Exception as e:
            return handle_error(e, "inlet", body)

    def outlet(self, body: Dict, __user__: Optional[Dict] = None) -> Dict:
        """
        Post-processes the response after execution.

        Args:
            body (Dict): The response payload.
            __user__ (Optional[Dict]): User metadata.

        Returns:
            Dict: Modified response payload.
        """
        try:
            logger.info(f"Outlet: Adjusting response data...")
            body["processed_output"] = True
            return body

        except Exception as e:
            return handle_error(e, "outlet", body)

    async def action(
        self,
        body: Dict,
        __user__: Optional[Dict] = None,
        __event_emitter__: Optional[Callable] = None,
        __event_call__: Optional[Callable] = None,
    ) -> Dict:
        """
        Handles interactive actions.

        Args:
            body (Dict): Action request data.
            __user__ (Optional[Dict]): User metadata.
            __event_emitter__ (Callable): Emits events.
            __event_call__ (Callable): Calls interactive events.

        Returns:
            Dict: Action response.
        """
        try:
            if __event_call__:
                user_response = await __event_call__(
                    {
                        "type": "input",
                        "data": {
                            "title": "Confirm Action",
                            "message": "Proceed with the operation?",
                            "placeholder": "yes/no",
                        },
                    }
                )

                return {"confirmation": user_response}

            return {"error": "No event call provided."}

        except Exception as e:
            return handle_error(e, "action", body)

    async def pipe(self, body: Dict, __user__: Dict, __request__: Request) -> Dict:
        """
        Processes requests with API integration.

        Args:
            body (Dict): The request payload.
            __user__ (Dict): User metadata.
            __request__ (Request): FastAPI request object.

        Returns:
            Dict: Processed response.
        """
        try:
            logger.info("Processing request in Pipe...")

            messages = body.get("messages", [])
            if not messages:
                return handle_error(ValueError("No input messages found"), "pipe", body)

            user_message = messages[-1].get("content", "")
            modified_query = f"Processed Query: {user_message}"

            response_data = await self.process_request(modified_query)

            body["messages"].append(
                {"role": "assistant", "content": json.dumps(response_data)}
            )
            return body

        except Exception as e:
            return handle_error(e, "pipe", body)


# Example Usage
if __name__ == "__main__":
    tool = Tools()

    async def test_tool():
        response = await tool.process_request("Example query")
        print(json.dumps(response, indent=4))

    import asyncio

    asyncio.run(test_tool())
```