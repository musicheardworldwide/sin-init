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
from fastapi import Request
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

    def pipe(self, body: Dict) -> Union[str, Generator, Iterator]:
        """
        Processes the request payload, modifying the message structure and calling an external API.

        Args:
            body (Dict): The OpenWebUI request payload.

        Returns:
            Union[str, Generator, Iterator]: The response, either as a string or a stream.
        """
        try:
            system_message, messages = pop_system_message(body["messages"])
            processed_messages = []

            for message in messages:
                processed_content = []
                if isinstance(message.get("content"), list):
                    for item in message["content"]:
                        if item["type"] == "text":
                            processed_content.append(
                                {"type": "text", "text": item["text"]}
                            )
                        elif item["type"] == "image_url":
                            processed_image = self.process_image(item)
                            processed_content.append(processed_image)
                else:
                    processed_content = [
                        {"type": "text", "text": message.get("content", "")}
                    ]

                processed_messages.append(
                    {"role": message["role"], "content": processed_content}
                )

            payload = {
                "model": body["model"],
                "messages": processed_messages,
                "max_tokens": body.get("max_tokens", 1024),
                "temperature": body.get("temperature", 0.7),
                "top_p": body.get("top_p", 0.9),
                "stream": body.get("stream", False),
                **({"system": str(system_message)} if system_message else {}),
            }

            headers = {
                "Authorization": f"Bearer {self.config.API_KEY}",
                "Content-Type": "application/json",
            }

            url = self.config.API_ENDPOINT

            if body.get("stream", False):
                return self.stream_response(url, headers, payload)
            else:
                return self.non_stream_response(url, headers, payload)

        except Exception as e:
            return handle_error(e, "pipe", body)

    def process_image(self, image_data: Dict) -> Dict:
        """
        Processes image data, ensuring it meets size requirements.

        Args:
            image_data (Dict): Image metadata from the OpenWebUI request.

        Returns:
            Dict: Processed image data.
        """
        try:
            if image_data["image_url"]["url"].startswith("data:image"):
                mime_type, base64_data = image_data["image_url"]["url"].split(",", 1)
                media_type = mime_type.split(":")[1].split(";")[0]
                image_size = len(base64_data) * 3 / 4  # Convert base64 size to bytes

                if image_size > self.config.MAX_IMAGE_SIZE:
                    raise ValueError(
                        f"Image exceeds 5MB limit: {image_size / (1024 * 1024):.2f}MB"
                    )

                return {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": base64_data,
                    },
                }
            else:
                url = image_data["image_url"]["url"]
                response = requests.head(url, allow_redirects=True)
                content_length = int(response.headers.get("content-length", 0))

                if content_length > self.config.MAX_IMAGE_SIZE:
                    raise ValueError(
                        f"Image at URL exceeds 5MB limit: {content_length / (1024 * 1024):.2f}MB"
                    )

                return {"type": "image", "source": {"type": "url", "url": url}}

        except Exception as e:
            return handle_error(e, "process_image", image_data)

    def stream_response(self, url: str, headers: Dict, payload: Dict) -> Generator:
        """
        Handles streaming responses from the API.

        Args:
            url (str): The API endpoint.
            headers (Dict): Request headers.
            payload (Dict): Request body.

        Returns:
            Generator: Streamed API response.
        """
        try:
            with requests.post(
                url, headers=headers, json=payload, stream=True, timeout=(3.05, 60)
            ) as response:
                if response.status_code != 200:
                    raise Exception(
                        f"HTTP Error {response.status_code}: {response.text}"
                    )

                for line in response.iter_lines():
                    if line:
                        yield line.decode("utf-8")

        except Exception as e:
            yield handle_error(e, "stream_response", payload)

    def non_stream_response(self, url: str, headers: Dict, payload: Dict) -> str:
        """
        Handles non-streaming API responses.

        Args:
            url (str): The API endpoint.
            headers (Dict): Request headers.
            payload (Dict): Request body.

        Returns:
            str: The response as a string.
        """
        try:
            response = requests.post(
                url, headers=headers, json=payload, timeout=(3.05, 60)
            )
            if response.status_code != 200:
                raise Exception(f"HTTP Error {response.status_code}: {response.text}")

            return response.json().get("response", "No response received.")

        except Exception as e:
            return handle_error(e, "non_stream_response", payload)


# Example Usage
if __name__ == "__main__":
    pipe = Pipe()

    async def test_pipe():
        test_request = {
            "messages": [{"role": "user", "content": "What is Open WebUI?"}]
        }

        response = pipe.pipe(test_request)
        if isinstance(response, Generator):
            for chunk in response:
                print(chunk)
        else:
            print(response)

    import asyncio

    asyncio.run(test_pipe())
