"""
title: OpenWebUI Advanced Action
author: Wes Caldwell
email: musicheardworldwide@gmail.com
author_url: https://github.com/musicheardworldwide
version: 1.0.0
license: MIT
description: A structured Open WebUI action for data visualization, API integration, and real-time UI updates.
requirements:
"""

import os
import json
import uuid
import logging
import time
import traceback
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from openai import OpenAI
from fastapi import Request
from open_webui.utils.misc import pop_system_message
from open_webui.models.files import Files

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
        "suggestion": "Check API configurations, file paths, and input values.",
    }


# Action Definition
class Action:
    """
    OpenWebUI Action function for data visualization and API integration.
    """

    class Valves(BaseModel):
        show_status: bool = Field(
            default=True, description="Show status updates in UI."
        )
        html_filename: str = Field(
            default="chart_visualization.html",
            description="Name of the generated HTML file.",
        )
        OPENAI_KEY: str = Field(
            default="", description="API key for OpenAI or Claude integration."
        )
        OPENAI_URL: str = Field(
            default="", description="API endpoint for OpenAI or Claude service."
        )

    SYSTEM_PROMPT_BUILD_CHARTS = """
    Objective:
    Your goal is to analyze the user's query, extract relevant data, and generate an appropriate chart.
    
    Steps:
    1. Identify the data provided in the query.
    2. Determine the best chart type (bar, pie, line, scatter, etc.).
    3. Generate clean, well-structured HTML with embedded JavaScript (Plotly).
    4. Ensure the chart scale is properly calibrated for readability.
    5. If no chart can be generated, return a fun HTML message.

    Constraints:
    - Output **only** HTML (no extra text or markdown).
    - Ensure numeric data is properly parsed and formatted.
    - If the data is invalid, return a fun HTML error message.
    """

    USER_PROMPT_GENERATE_HTML = """
    Given this user query: {Query}, generate the corresponding HTML with an embedded chart.
    """

    def __init__(self):
        self.valves = self.Valves()
        self.openai = None
        self.html_content = ""

    def create_or_get_file(self, user_id: str, html_content: str) -> str:
        """
        Creates or retrieves an HTML file for visualization.

        Args:
            user_id (str): The ID of the user.
            html_content (str): The generated HTML content.

        Returns:
            str: The ID of the stored file.
        """
        try:
            filename = f"{int(time.time() * 1000)}_{self.valves.html_filename}"
            directory = "action_embed"

            logger.debug(f"Checking existing files for user: {user_id}")

            # Check if the file already exists
            existing_files = Files.get_files()
            for file in existing_files:
                if (
                    file.filename == f"{directory}/{user_id}/{filename}"
                    and file.user_id == user_id
                ):
                    logger.debug(f"Existing file found. Updating content.")
                    self.update_html_content(file.meta["path"], html_content)
                    return file.id

            # Create new file
            base_path = os.path.join("uploads", directory)
            os.makedirs(base_path, exist_ok=True)
            file_path = os.path.join(base_path, filename)

            logger.debug(f"Creating new file at: {file_path}")
            self.update_html_content(file_path, html_content)

            file_id = str(uuid.uuid4())
            meta = {
                "source": file_path,
                "title": "Chart Visualization",
                "content_type": "text/html",
                "size": os.path.getsize(file_path),
                "path": file_path,
            }

            file_data = {
                "id": file_id,
                "filename": f"{directory}/{user_id}/{filename}",
                "meta": meta,
            }
            new_file = Files.insert_new_file(user_id, file_data)
            logger.debug(f"New file created with ID: {new_file.id}")
            return new_file.id

        except Exception as e:
            return handle_error(
                e,
                "create_or_get_file",
                {"user_id": user_id, "html_content": html_content},
            )

    def update_html_content(self, file_path: str, html_content: str):
        """
        Updates or writes new HTML content to a file.

        Args:
            file_path (str): Path to the file.
            html_content (str): The HTML content to write.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.debug(f"HTML content saved at: {file_path}")

        except Exception as e:
            return handle_error(
                e,
                "update_html_content",
                {"file_path": file_path, "html_content": html_content},
            )

    async def action(
        self,
        body: dict,
        __user__=None,
        __event_emitter__=None,
        __event_call__=None,
    ) -> Optional[dict]:
        """
        Executes the action, generating a chart and embedding it into a response.

        Args:
            body (dict): Request payload.
            __user__ (dict): User metadata.
            __event_emitter__ (Callable): Emits status updates to the UI.

        Returns:
            dict: Updated request body with HTML embed tag.
        """
        try:
            logger.info("Action started: Generating visualization")

            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "Analyzing data...", "done": False},
                    }
                )

            original_content = body["messages"][-1]["content"]
            self.openai = OpenAI(
                api_key=self.valves.OPENAI_KEY, base_url=self.valves.OPENAI_URL
            )

            response = self.openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT_BUILD_CHARTS},
                    {
                        "role": "user",
                        "content": self.USER_PROMPT_GENERATE_HTML.format(
                            Query=original_content
                        ),
                    },
                ],
                max_tokens=1000,
                temperature=0.7,
            )

            html_content = response.choices[0].message.content
            user_id = __user__["id"]
            file_id = self.create_or_get_file(user_id, html_content)

            body["messages"][-1]["content"] += f"\n\n{{{{HTML_FILE_ID_{file_id}}}}}"

            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Chart ready!", "done": True},
                }
            )
            logger.info("Action completed successfully")

        except Exception as e:
            return handle_error(e, "action", body)

        return body
