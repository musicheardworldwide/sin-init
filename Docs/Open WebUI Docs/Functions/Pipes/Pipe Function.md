Okay, this is a well-structured Python script designed as an "OpenWebUI Pipe." Let's break it down section by section. This type of pipe is meant to intercept requests from OpenWebUI, process them (potentially by calling an external API), and then return a response, possibly streamed.

**Script Breakdown for [[sin/1. Initialization/Tools/MCP Server Tools/Obsidian/Obsidian|Obsidian]] Documentation:**

```markdown
# OpenWebUI Advanced Pipe

**File:** `openwebui_advanced_pipe.py` (Assuming a filename)
**Author:** Wes Caldwell
**Email:** musicheardworldwide@gmail.com
**Author URL:** https://github.com/musicheardworldwide
**Version:** 1.0.0
**License:** MIT
**Description:** A structured Open WebUI pipe for API integration, with streaming and advanced error handling.
**Requirements:** (Note: This section is empty in the script. You might want to fill it with `requests`, `pydantic`, `fastapi`, `open-webui`)

---

## 1. Overview

This script defines a custom "Pipe" for OpenWebUI. Its primary purpose is to act as an intermediary that receives requests from OpenWebUI, transforms them, sends them to an external API, and then streams or returns the API's response back to OpenWebUI. It includes robust error handling, configuration management via Pydantic, and support for processing text and image inputs.

---

## 2. Imports

The script utilizes several standard and third-party libraries:

*   **Standard Libraries:**
    *   `os`: (Not directly used in the provided snippet, but often included for environment variables)
    *   `json`: For working with JSON data.
    *   `logging`: For application logging.
    *   `requests`: For making HTTP requests to the external API.
    *   `time`: (Not directly used in the provided snippet, but often for delays or timestamps)
    *   `traceback`: For generating stack traces during error handling.
    *   `typing`: For type hinting (`Optional`, `Dict`, `Generator`, `Union`, `Iterator`).
*   **Third-Party Libraries:**
    *   `pydantic`: For data validation and settings management (`BaseModel`, `Field`).
    *   `fastapi`: (Specifically `Request`, though not directly used in the `Pipe` class logic, it implies the context this pipe might run in or be tested with).
    *   `open_webui.utils.misc`: For `pop_system_message`, a utility likely specific to OpenWebUI for message processing.

---

## 3. Logging Configuration

*   A logger named `__name__` (which will be the module's name) is configured.
*   It uses a `StreamHandler` to output logs to the console.
*   A specific `Formatter` (`%(asctime)s - %(levelname)s - %(message)s`) is applied.
*   The default log level is set to `INFO`.
*   This setup ensures that logs are only configured once, even if the module is imported multiple times.

```python
# Configure Logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

---

## 4. Centralized Error Handling (`handle_error` function)

[[handle_error]]

*   **Purpose:** Provides a consistent way to catch exceptions and format them into a structured dictionary suitable for OpenWebUI to display or process.
*   **Arguments:**
    *   `exception (Exception)`: The exception object that was caught.
    *   `function_name (str)`: The name of the function where the error occurred.
    *   `inputs (dict)`: The original inputs to the function, useful for debugging.
*   **Functionality:**
    1.  Logs the error message and a detailed stack trace.
    2.  Returns a dictionary containing:
        *   `error: True`
        *   `function`: Name of the failing function.
        *   `message`: The error message.
        *   `stack_trace`: The full stack trace.
        *   `inputs`: The original inputs.
        *   `suggestion`: A generic troubleshooting suggestion.
*   **Usage:** This function is called within `try...except` blocks in other parts of the script.

```python
def handle_error(exception: Exception, function_name: str, inputs: dict) -> dict:
    # ... implementation ...
```

---

## 5. `Pipe` Class

[[Pipe]]

This class encapsulates the core logic of the OpenWebUI pipe.

### 5.1. `Config` Inner Class (Pydantic Model)

[[Pipe.Config]]

*   **Purpose:** Defines and validates configuration parameters for the `Pipe`. Uses Pydantic for type checking and default values.
*   **Fields:**
    *   `API_ENDPOINT (str)`: The URL of the external API. (Default: `https://api.example.com/process`)
    *   `API_KEY (str)`: The API key for authenticating with the external API. (Default: `""`)
    *   `MAX_IMAGE_SIZE (int)`: Maximum allowed image size in bytes. (Default: 5MB)

```python
class Config(BaseModel):
    API_ENDPOINT: str = Field(...)
    API_KEY: str = Field(...)
    MAX_IMAGE_SIZE: int = Field(...)
```

### 5.2. `__init__(self)`

[[Pipe.__init__]]

*   **Purpose:** Initializes an instance of the `Pipe` class.
*   **Functionality:** Creates an instance of the `Pipe.Config` class and stores it in `self.config`. This makes configuration values accessible throughout the `Pipe` instance.

```python
def __init__(self):
    self.config = self.Config()
```

### 5.3. `pipe(self, body: Dict)` Method

[[Pipe.pipe]]

*   **Purpose:** This is the main entry point for the pipe. It receives the request body from OpenWebUI, processes it, interacts with an external API, and returns the result.
*   **Arguments:**
    *   `body (Dict)`: The request payload from OpenWebUI. Expected to contain keys like `messages`, `model`, `stream`, etc.
*   **Returns:**
    *   `Union[str, Generator, Iterator]`: Either a string (for non-streamed responses) or a generator/iterator (for streamed responses). Can also return an error dictionary from `handle_error`.
*   **Core Logic:**
    1.  **Message Preprocessing:**
        *   Uses `pop_system_message` from `open_webui.utils.misc` to separate the system message (if any) from the user/assistant messages.
        *   Iterates through each message in `body["messages"]`.
        *   If a message's content is a list (indicating multi-modal content like text and images):
            *   Text parts are added directly.
            *   Image parts (`item["type"] == "image_url"`) are processed by calling `self.process_image(item)`.
        *   If a message's content is a string, it's wrapped as a text part.
        *   The processed messages are collected.
    2.  **API Payload Construction:**
        *   Constructs a `payload` dictionary for the external API, including:
            *   `model`, `messages` (the processed ones), `max_tokens`, `temperature`, `top_p`, `stream`.
            *   The `system_message` is added if present.
    3.  **API Request:**
        *   Sets `headers` including `Authorization` (with `self.config.API_KEY`) and `Content-Type`.
        *   Retrieves the `url` from `self.config.API_ENDPOINT`.
        *   **Conditional Streaming:**
            *   If `body.get("stream", False)` is `True`, it calls `self.stream_response()` to handle the API call as a stream.
            *   Otherwise, it calls `self.non_stream_response()` for a regular, non-streamed API call.
    4.  **Error Handling:**
        *   The entire method is wrapped in a `try...except` block. If any exception occurs, it calls `handle_error(e, "pipe", body)`.

### 5.4. `process_image(self, image_data: Dict)` Method

[[Pipe.process_image]]

*   **Purpose:** Processes image data provided in the OpenWebUI request, validating its size and converting it to a format suitable for the external API.
*   **Arguments:**
    *   `image_data (Dict)`: A dictionary representing an image, typically containing an `image_url` field which can be a data URI or a remote URL.
*   **Returns:**
    *   `Dict`: A dictionary representing the processed image, or an error dictionary from `handle_error`.
*   **Logic:**
    1.  **Base64 Encoded Images:**
        *   If `image_data["image_url"]["url"]` starts with `data:image`:
            *   Extracts `mime_type` and `base64_data`.
            *   Calculates `image_size` from the base64 string.
            *   Checks if `image_size` exceeds `self.config.MAX_IMAGE_SIZE`. Raises `ValueError` if too large.
            *   Returns a dictionary with `type: "image"`, `source: {"type": "base64", "media_type": ..., "data": ...}`.
    2.  **Image URLs:**
        *   If it's a regular URL:
            *   Makes a `requests.head()` request to get image headers (specifically `content-length`) without downloading the full image.
            *   Checks if `content_length` exceeds `self.config.MAX_IMAGE_SIZE`. Raises `ValueError` if too large.
            *   Returns a dictionary with `type: "image"`, `source: {"type": "url", "url": ...}`.
    3.  **Error Handling:**
        *   Wrapped in `try...except`. Calls `handle_error(e, "process_image", image_data)` on failure.

### 5.5. `stream_response(self, url: str, headers: Dict, payload: Dict)` Method

[[Pipe.stream_response]]

*   **Purpose:** Handles making a streaming POST request to the external API and yielding the response line by line.
*   **Arguments:**
    *   `url (str)`: The API endpoint.
    *   `headers (Dict)`: Request headers.
    *   `payload (Dict)`: Request body.
*   **Returns:**
    *   `Generator`: Yields decoded lines from the streaming API response.
    *   If an error occurs, it yields a single item: the error dictionary from `handle_error`.
*   **Logic:**
    1.  Makes a `requests.post` request with `stream=True` and a timeout (`(3.05, 60)` connect and read timeout respectively).
    2.  Checks if `response.status_code` is not 200. If so, raises an exception with the error details.
    3.  Iterates over `response.iter_lines()`. For each non-empty line, it decodes it (UTF-8) and `yield`s it.
    4.  **Error Handling:**
        *   Wrapped in `try...except`. On failure, it `yield`s the result of `handle_error(e, "stream_response", payload)`.

### 5.6. `non_stream_response(self, url: str, headers: Dict, payload: Dict)` Method

[[Pipe.non_stream_response]]

*   **Purpose:** Handles making a non-streaming POST request to the external API and returns the full response.
*   **Arguments:**
    *   `url (str)`: The API endpoint.
    *   `headers (Dict)`: Request headers.
    *   `payload (Dict)`: Request body.
*   **Returns:**
    *   `str`: The content of the API's response (specifically, the value of the "response" key in the JSON, or a default message).
    *   If an error occurs, it returns the error dictionary from `handle_error`.
*   **Logic:**
    1.  Makes a `requests.post` request with a timeout.
    2.  Checks if `response.status_code` is not 200. If so, raises an exception.
    3.  Parses the JSON response and attempts to return `response.json().get("response", "No response received.")`.
    4.  **Error Handling:**
        *   Wrapped in `try...except`. On failure, it `return`s the result of `handle_error(e, "non_stream_response", payload)`.

---

## 6. Example Usage (`if __name__ == "__main__":`)

*   **Purpose:** Provides a simple way to test the `Pipe` class directly when the script is run.
*   **Functionality:**
    1.  Creates an instance of `Pipe`.
    2.  Defines an `async` function `test_pipe()` (Note: the `Pipe.pipe` method itself is synchronous, but the test wrapper is async, perhaps for compatibility with environments where pipes are tested or run asynchronously).
    3.  Creates a sample `test_request` dictionary.
    4.  Calls `pipe.pipe(test_request)`.
    5.  If the response is a `Generator` (streamed), it iterates through and prints each chunk.
    6.  Otherwise (non-streamed), it prints the whole response.
    7.  Uses `asyncio.run(test_pipe())` to execute the async test function.

```python
if __name__ == "__main__":
    pipe = Pipe()

    async def test_pipe():
        # ... test logic ...

    import asyncio
    asyncio.run(test_pipe())
```

---

## 7. Key Components and Flow for Graphing

*   **Entry Point:** [[Pipe.pipe]]
    *   Reads `body` (OpenWebUI request).
    *   Uses [[open_webui.utils.misc.pop_system_message]] (External Dependency/Util).
    *   For image messages, calls [[Pipe.process_image]].
        *   [[Pipe.process_image]] may call `requests.head()` (External HTTP).
        *   [[Pipe.process_image]] uses [[Pipe.Config]] for `MAX_IMAGE_SIZE`.
        *   [[Pipe.process_image]] calls [[handle_error]] on exceptions.
    *   Constructs API `payload`.
    *   Uses [[Pipe.Config]] for `API_ENDPOINT` and `API_KEY`.
    *   Conditionally calls either:
        *   [[Pipe.stream_response]]
            *   Calls `requests.post(stream=True)` (External HTTP).
            *   Yields responses or [[handle_error]] result.
        *   [[Pipe.non_stream_response]]
            *   Calls `requests.post()` (External HTTP).
            *   Returns response string or [[handle_error]] result.
    *   [[Pipe.pipe]] calls [[handle_error]] on its own exceptions.
*   **Configuration:** [[Pipe.Config]] (Pydantic model) is instantiated in [[Pipe.__init__]].
*   **Error Handling:** All major operations delegate to [[handle_error]] on exceptions.
*   **Logging:** [[logger]] is used by [[handle_error]].

This structure allows for clear linking in Obsidian. For example, `[[Pipe.pipe]]` would link to the section describing the `pipe` method.

---
```

This breakdown provides a detailed view of each part of the script, its purpose, and how it interacts with other components, making it suitable for documentation in Obsidian and for an LLM to understand its structure and functionality.

Now, here is the complete script as requested:

```python
"""
title: OpenWebUI Advanced Pipe
author: Wes Caldwell
email: musicheardworldwide@gmail.com
author_url: https://github.com/musicheardworldwide
version: 1.0.0
license: MIT
description: A structured Open WebUI pipe for API integration, with streaming and advanced error handling.
requirements:
"""

import os
import json
import logging
import requests
import time
import traceback
from typing import Optional, Dict, Generator, Union, Iterator
from pydantic import BaseModel, Field
from fastapi import Request # Note: Request is imported but not directly used in the Pipe class logic itself.
                           # It might be relevant for the broader context where this pipe is deployed or tested.
from open_webui.utils.misc import pop_system_message

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
        "suggestion": "Check API configurations, input values, and connection settings.",
    }


# Pipe Definition
class Pipe:
    """
    OpenWebUI Pipe function for API integration, streaming responses, and structured processing.
    """

    class Config(BaseModel):
        API_ENDPOINT: str = Field(
            default="https://api.example.com/process",
            description="External API endpoint for processing queries",
        )
        API_KEY: str = Field(default="", description="API key for authentication")
        MAX_IMAGE_SIZE: int = Field(
            default=5 * 1024 * 1024, description="Maximum image size allowed (5MB)"
        )

    def __init__(self):
        self.config = self.Config()
        # API_KEY could also be loaded from environment variables here if desired,
        # for example: self.config.API_KEY = os.getenv("MY_API_KEY", self.config.API_KEY)

    def pipe(self, body: Dict) -> Union[str, Generator, Iterator]:
        """
        Processes the request payload, modifying the message structure and calling an external API.

        Args:
            body (Dict): The OpenWebUI request payload. Expected to have keys like 'messages', 'model', 'stream'.

        Returns:
            Union[str, Generator, Iterator]: The response, either as a string or a stream.
        """
        try:
            # Validate that 'messages' key exists and is a list
            if "messages" not in body or not isinstance(body["messages"], list):
                raise ValueError("Request body must contain a 'messages' list.")

            system_message_obj, messages_list = pop_system_message(body["messages"])
            system_message_text = str(system_message_obj) if system_message_obj else None
            
            processed_messages = []

            for message in messages_list:
                processed_content_list = []
                content = message.get("content")

                if isinstance(content, list): # Handle multi-modal content (list of dicts)
                    for item in content:
                        if item.get("type") == "text":
                            processed_content_list.append(
                                {"type": "text", "text": item.get("text", "")}
                            )
                        elif item.get("type") == "image_url":
                            # Ensure image_url is a dict with a 'url' key
                            if isinstance(item.get("image_url"), dict) and "url" in item["image_url"]:
                                processed_image = self.process_image(item) # Pass the whole item
                                processed_content_list.append(processed_image)
                            else:
                                logger.warning(f"Skipping malformed image_url item: {item}")
                        else:
                            logger.warning(f"Skipping unknown content item type: {item.get('type')}")
                elif isinstance(content, str): # Handle simple text content
                    processed_content_list = [
                        {"type": "text", "text": content}
                    ]
                else: # If content is neither list nor string, or is None/empty
                    logger.warning(f"Message content is not a list or string, or is empty: {content}")
                    # Add an empty text content if required by downstream API, or skip
                    processed_content_list = [{"type": "text", "text": ""}]


                processed_messages.append(
                    {"role": message.get("role", "user"), "content": processed_content_list}
                )

            payload = {
                "model": body.get("model", "default-model"), # Provide a default if not present
                "messages": processed_messages,
                "max_tokens": body.get("max_tokens", 1024),
                "temperature": body.get("temperature", 0.7),
                "top_p": body.get("top_p", 0.9),
                "stream": body.get("stream", False),
                **({"system": system_message_text} if system_message_text else {}),
            }

            headers = {
                "Authorization": f"Bearer {self.config.API_KEY}",
                "Content-Type": "application/json",
            }

            url = self.config.API_ENDPOINT

            if not url:
                raise ValueError("API_ENDPOINT is not configured.")
            if not self.config.API_KEY: # Optional: decide if API key is strictly required
                logger.warning("API_KEY is not configured. Proceeding without authentication.")


            if body.get("stream", False):
                return self.stream_response(url, headers, payload)
            else:
                return self.non_stream_response(url, headers, payload)

        except Exception as e:
            return handle_error(e, "pipe", body)

    def process_image(self, image_item: Dict) -> Dict:
        """
        Processes image data, ensuring it meets size requirements.
        Expects image_item to be a dict like: {"type": "image_url", "image_url": {"url": "data:..." or "http://..."}}

        Args:
            image_item (Dict): Image metadata from the OpenWebUI request.

        Returns:
            Dict: Processed image data suitable for an API, or an error dict.
        """
        try:
            image_url_data = image_item.get("image_url", {})
            url_string = image_url_data.get("url")

            if not url_string or not isinstance(url_string, str):
                raise ValueError("Image item is missing 'url' or URL is not a string.")

            if url_string.startswith("data:image"):
                # data:[<mediatype>][;base64],<data>
                try:
                    header, base64_data = url_string.split(",", 1)
                    mime_type_full = header.split(":")[1] # e.g., image/png;base64
                    media_type = mime_type_full.split(";")[0] # e.g., image/png
                except ValueError:
                    raise ValueError("Malformed data URI for image.")

                # Estimate size: Base64 encoding increases size by roughly 4/3.
                # This calculation is an approximation.
                image_size = (len(base64_data) * 3 / 4) - base64_data.count('=')


                if image_size > self.config.MAX_IMAGE_SIZE:
                    raise ValueError(
                        f"Base64 image exceeds {self.config.MAX_IMAGE_SIZE // (1024*1024)}MB limit: {image_size / (1024 * 1024):.2f}MB"
                    )

                return {
                    "type": "image", # Changed from "image_url" to "image" as per common API conventions
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64_data,
                    },
                }
            elif url_string.startswith("http://") or url_string.startswith("https://"):
                try:
                    response = requests.head(url_string, allow_redirects=True, timeout=10)
                    response.raise_for_status() # Check for HTTP errors
                    content_length = int(response.headers.get("content-length", 0))

                    if content_length == 0:
                        logger.warning(f"Content-Length for image URL {url_string} is 0 or not provided. Size check might be inaccurate.")
                        # Optionally, you could try a GET request for a small chunk if really needed, but 'head' is preferred.

                    if content_length > self.config.MAX_IMAGE_SIZE:
                        raise ValueError(
                            f"Image at URL {url_string} exceeds {self.config.MAX_IMAGE_SIZE // (1024*1024)}MB limit: {content_length / (1024 * 1024):.2f}MB"
                        )
                    
                    return {"type": "image", "source": {"type": "url", "url": url_string}}


                except requests.exceptions.RequestException as e:
                    raise ValueError(f"Failed to fetch image headers from URL {url_string}: {e}")

            else:
                raise ValueError(f"Unsupported image URL scheme: {url_string[:30]}...")


        except Exception as e:
            # When process_image is called from pipe method, pipe's error handler will catch this.
            # However, if process_image is called standalone, we might want its own error dict.
            # For consistency with other methods, let's make it return the error dict.
            return handle_error(e, "process_image", {"image_item": image_item})


    def stream_response(self, url: str, headers: Dict, payload: Dict) -> Generator[str, None, None]:
        """
        Handles streaming responses from the API.

        Args:
            url (str): The API endpoint.
            headers (Dict): Request headers.
            payload (Dict): Request body.

        Yields:
            str: Chunks of the API response.
        """
        try:
            with requests.post(
                url, headers=headers, json=payload, stream=True, timeout=(10, 60) # (connect_timeout, read_timeout)
            ) as response:
                if response.status_code != 200:
                    # Attempt to get more detailed error from response body
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        error_detail = error_json.get("error", {}).get("message", response.text)
                    except json.JSONDecodeError:
                        pass # Use raw text if not JSON
                    raise Exception(
                        f"API Error {response.status_code}: {error_detail}"
                    )

                for line in response.iter_lines():
                    if line:
                        yield line.decode("utf-8") + "\n" # Add newline as iter_lines strips it

        except Exception as e:
            # For generators, yielding the error is a common pattern.
            # The caller needs to check if the yielded item is an error dict.
            error_handled = handle_error(e, "stream_response", {"url": url, "payload_keys": list(payload.keys())})
            yield json.dumps(error_handled) + "\n"


    def non_stream_response(self, url: str, headers: Dict, payload: Dict) -> Union[str, Dict]:
        """
        Handles non-streaming API responses.

        Args:
            url (str): The API endpoint.
            headers (Dict): Request headers.
            payload (Dict): Request body.

        Returns:
            Union[str, Dict]: The response as a string (or Dict if API returns structured JSON), or an error Dict.
        """
        try:
            response = requests.post(
                url, headers=headers, json=payload, timeout=(10, 60)
            )
            if response.status_code != 200:
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = error_json.get("error", {}).get("message", response.text)
                except json.JSONDecodeError:
                    pass
                raise Exception(f"API Error {response.status_code}: {error_detail}")

            # Assuming the external API returns JSON with a "response" field for the main content.
            # Or it might return the full JSON if no "response" field is found.
            try:
                json_response = response.json()
                # This part depends heavily on the actual API response structure
                # If the API returns a simple string in 'response' field:
                # return json_response.get("response", "No 'response' field in JSON.")
                # If the API returns a more complex object that should be passed through:
                return json_response # Or specific parts of it
            except json.JSONDecodeError:
                # If response is not JSON, return as text
                return response.text if response.text else "No content received."


        except Exception as e:
            return handle_error(e, "non_stream_response", {"url": url, "payload_keys": list(payload.keys())})


# Example Usage
if __name__ == "__main__":
    # This example assumes you have an API endpoint that behaves like an LLM API
    # For a real test, you might need to mock `requests.post` or set up a test server.

    pipe = Pipe()

    # Example: Override config for local testing if needed
    # pipe.config.API_ENDPOINT = "http://localhost:8000/test-api" # A mock server
    # pipe.config.API_KEY = "test_key"

    async def test_pipe_streaming():
        print("\n--- Testing Streaming Response ---")
        test_request_stream = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "Tell me a story, stream it."}],
            "stream": True,
            "max_tokens": 50,
        }
        response_generator = pipe.pipe(test_request_stream)
        
        if isinstance(response_generator, Generator):
            print("Streaming response:")
            for chunk in response_generator:
                # Check if the chunk is an error dictionary (as yielded by stream_response on error)
                try:
                    # Attempt to parse as JSON, as error messages from stream_response are JSON strings
                    potential_error = json.loads(chunk)
                    if isinstance(potential_error, dict) and potential_error.get("error"):
                        print(f"STREAM ERROR: {potential_error['message']}")
                        break 
                except json.JSONDecodeError:
                    pass # Not a JSON error message, print as is
                
                print(chunk, end="")
            print("\n--- End of Stream ---")
        elif isinstance(response_generator, dict) and response_generator.get("error"):
            print(f"Error during pipe setup for streaming: {response_generator['message']}")
        else:
            print(f"Unexpected response type for streaming: {type(response_generator)}")


    async def test_pipe_non_streaming():
        print("\n--- Testing Non-Streaming Response ---")
        test_request_non_stream = {
            "model": "test-model",
            "messages": [{"role": "user", "content": "What is Open WebUI in one sentence?"}],
            "stream": False,
        }
        response_data = pipe.pipe(test_request_non_stream)
        
        print("Non-streaming response:")
        if isinstance(response_data, dict) and response_data.get("error"):
            print(f"ERROR: {response_data['message']}")
            if "stack_trace" in response_data:
                print(f"Trace: {response_data['stack_trace'][:200]}...") # Print snippet
        elif isinstance(response_data, (str, dict, list)): # Assuming API can return various JSON structures
            print(json.dumps(response_data, indent=2) if not isinstance(response_data, str) else response_data)
        else:
            print(f"Unexpected response type: {type(response_data)}")


    async def test_pipe_with_image_base64():
        print("\n--- Testing with Base64 Image (Non-Streaming) ---")
        # A tiny (1x1 pixel) transparent PNG as a base64 string
        tiny_png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        test_request_image = {
            "model": "test-vision-model",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image?"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{tiny_png_base64}"}}
                    ]
                }
            ],
            "stream": False,
        }
        response_data = pipe.pipe(test_request_image)
        print("Image (Base64) response:")
        if isinstance(response_data, dict) and response_data.get("error"):
            print(f"ERROR: {response_data['message']}")
        else:
            print(json.dumps(response_data, indent=2) if not isinstance(response_data, str) else response_data)


    async def main_tests():
        # Note: These tests will likely fail if API_ENDPOINT is "https://api.example.com/process"
        # and no valid API_KEY is set, or if that endpoint doesn't exist or expect these payloads.
        # This is for demonstration of calling the pipe.
        
        # await test_pipe_streaming()
        # await test_pipe_non_streaming()
        await test_pipe_with_image_base64() # This will likely fail on api.example.com

        # Test error handling for invalid image URL
        print("\n--- Testing Invalid Image URL ---")
        invalid_image_request = {
             "model": "test-vision-model",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is in this image?"},
                        {"type": "image_url", "image_url": {"url": f"http://nonexistentdomain123abc.com/image.jpg"}}
                    ]
                }
            ],
            "stream": False,
        }
        response_data = pipe.pipe(invalid_image_request)
        print("Invalid Image URL response:")
        if isinstance(response_data, dict) and response_data.get("error"):
            print(f"EXPECTED ERROR: {response_data['message']}")
        else:
            print("UNEXPECTED SUCCESS or different error format.")
            print(json.dumps(response_data, indent=2) if not isinstance(response_data, str) else response_data)


    import asyncio
    # To run these tests, you might need to set up a mock server or adjust API_ENDPOINT/API_KEY.
    # For now, we'll just show the structure.
    # For actual execution and output, you'd uncomment the asyncio.run call.
    # asyncio.run(main_tests())
    print("Example tests defined. Uncomment 'asyncio.run(main_tests())' to execute.")
    print(f"Current API Endpoint: {pipe.config.API_ENDPOINT}")
    print(f"API Key Set: {'Yes' if pipe.config.API_KEY else 'No'}")

```