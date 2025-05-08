Okay, let's break down this "OpenWebUI Advanced Action" script. This script defines an action that can be triggered within OpenWebUI, likely to generate visualizations (charts) based on user input by querying an [[sin/Initialization/Docs/Datasets/8. Datasets|8. Datasets]] (like OpenAI or Claude) and then embedding the resulting HTML into the chat.

**Script Breakdown for [[sin/Initialization/Tools/MCP Server Tools/Obsidian/Obsidian|Obsidian]] Documentation:**

```markdown
# OpenWebUI Advanced Action

**File:** `openwebui_advanced_action.py` (Assuming a filename)
**Author:** Wes Caldwell
**Email:** musicheardworldwide@gmail.com
**Author URL:** https://github.com/musicheardworldwide
**Version:** 1.0.0
**License:** MIT
**Description:** A structured Open WebUI action for data visualization, API integration, and real-time UI updates.
**Requirements:** (Note: This section is empty. You might list `openai`, `pydantic`, `fastapi`, `open-webui`)

---

## 1. Overview

This script defines a custom "Action" for OpenWebUI. Its primary function is to interpret a user's query, use an external Large Language Model (LLM) like OpenAI or Claude to generate HTML content (specifically a chart using Plotly.js), save this HTML to a file managed by OpenWebUI, and then embed a reference to this file in the chat response. This allows for dynamic data visualization within the OpenWebUI interface. The action includes configuration options, error handling, and real-time UI status updates.

---

## 2. Imports

The script utilizes several libraries:

*   **Standard Libraries:**
    *   `os`: For path manipulation (e.g., creating directories, joining paths).
    *   `json`: (Not directly used in the provided snippet, but often for data interchange).
    *   `uuid`: For generating unique file IDs.
    *   `logging`: For application logging.
    *   `time`: For generating timestamps (used in filenames).
    *   `traceback`: For generating stack traces during error handling.
    *   `typing`: For type hinting (`Optional`, `Dict`, `Any`).
*   **Third-Party Libraries:**
    *   `pydantic`: For data validation and settings management (`BaseModel`, `Field`).
    *   `openai`: The official OpenAI Python client library, used here potentially for Claude or other compatible APIs as well.
    *   `fastapi`: (Specifically `Request`, though not directly used in the `Action` class logic, it implies the context).
*   **OpenWebUI Specific Libraries:**
    *   `open_webui.utils.misc`: For `pop_system_message` (though not explicitly used in the `action` method shown, it might be part of a larger context or an unused import).
    *   `open_webui.models.files`: For `Files`, an OpenWebUI utility to manage user-uploaded/generated files.

---

## 3. Logging Configuration

*   A standard logger is configured, identical to the previous script.
*   It outputs to the console with a specific format and `INFO` level.

```python
# Configure Logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    # ... (formatter and handler setup) ...
logger.setLevel(logging.INFO)
```

---

## 4. Centralized Error Handling (`handle_error` function)

[[handle_error]]

*   **Purpose:** Provides a consistent way to catch exceptions and format them into a structured dictionary for OpenWebUI.
*   **Functionality:** Identical to the `handle_error` function in the "OpenWebUI Advanced Pipe" script. Logs the error and returns a detailed error dictionary.
*   **Usage:** Called within `try...except` blocks in the `Action` class methods.

```python
def handle_error(exception: Exception, function_name: str, inputs: dict) -> dict:
    # ... implementation ...
```

---

## 5. `Action` Class

[[Action]]

This class encapsulates the logic for the data visualization action.

### 5.1. `Valves` Inner Class (Pydantic Model)

[[Action.Valves]]

*   **Purpose:** Defines and validates configuration parameters for the `Action`, similar to a settings panel in OpenWebUI.
*   **Fields:**
    *   `show_status (bool)`: Whether to show status updates in the UI during action execution. (Default: `True`)
    *   `html_filename (str)`: Default name for the generated HTML file. (Default: `"chart_visualization.html"`)
    *   `OPENAI_KEY (str)`: API key for the LLM service (OpenAI, Claude, etc.). (Default: `""`)
    *   `OPENAI_URL (str)`: Base URL for the LLM API endpoint. (Default: `""`)

```python
class Valves(BaseModel):
    show_status: bool = Field(...)
    html_filename: str = Field(...)
    OPENAI_KEY: str = Field(...)
    OPENAI_URL: str = Field(...)
```

### 5.2. System and User Prompts (Constants)

[[Action.SYSTEM_PROMPT_BUILD_CHARTS]]
[[Action.USER_PROMPT_GENERATE_HTML]]

*   **`SYSTEM_PROMPT_BUILD_CHARTS (str)`:** A detailed system prompt instructing the LLM on how to behave. It specifies the objective (analyze query, generate chart), steps (identify data, choose chart type, generate HTML/Plotly, calibrate scale, handle no-chart case), and constraints (HTML-only output, parse numeric data, fun error message).
*   **`USER_PROMPT_GENERATE_HTML (str)`:** A template for the user prompt to the LLM. It takes the user's actual query (`{Query}`) as input.

### 5.3. `__init__(self)`

[[Action.__init__]]

*   **Purpose:** Initializes an instance of the `Action` class.
*   **Functionality:**
    *   Creates an instance of `self.Valves()` and stores it in `self.valves`.
    *   Initializes `self.openai` to `None` (it will be instantiated later in the `action` method).
    *   Initializes `self.html_content` to an empty string (this variable seems unused later, the content is passed directly).

```python
def __init__(self):
    self.valves = self.Valves()
    self.openai = None
    self.html_content = "" # Note: self.html_content appears to be unused.
```

### 5.4. `create_or_get_file(self, user_id: str, html_content: str)` Method

[[Action.create_or_get_file]]

*   **Purpose:** Manages the creation or updating of the HTML file that will store the generated chart. It interacts with OpenWebUI's file management system.
*   **Arguments:**
    *   `user_id (str)`: The ID of the user initiating the action.
    *   `html_content (str)`: The HTML content generated by the LLM.
*   **Returns:**
    *   `str`: The ID of the stored file in OpenWebUI's system.
    *   `dict`: An error dictionary from `handle_error` if an exception occurs.
*   **Core Logic:**
    1.  Generates a `filename` using a timestamp and `self.valves.html_filename`.
    2.  Defines a target `directory` ("action_embed").
    3.  **File Existence Check:** Iterates through `Files.get_files()` to see if a file with the constructed path-like name (`f"{directory}/{user_id}/{filename}"`) already exists for this `user_id`.
        *   *Note: This check might be inefficient if there are many files. A direct lookup by a unique identifier or a more targeted query would be better if OpenWebUI's `Files` model supports it.*
    4.  **If File Exists:** Calls `self.update_html_content()` to overwrite the existing file's content on disk. Returns the existing `file.id`.
    5.  **If File Doesn't Exist (New File):**
        *   Constructs the full `file_path` within the `uploads/action_embed` directory.
        *   Ensures the directory exists using `os.makedirs(base_path, exist_ok=True)`.
        *   Calls `self.update_html_content()` to write the `html_content` to the new file.
        *   Generates a new `file_id` using `uuid.uuid4()`.
        *   Prepares `meta` data for the file (source path, title, content type, size, actual disk path).
        *   Creates `file_data` dictionary.
        *   Calls `Files.insert_new_file(user_id, file_data)` to register the new file in OpenWebUI's system.
        *   Returns the `new_file.id`.
    6.  **Error Handling:** Wrapped in `try...except`, calls `handle_error` on failure.

### 5.5. `update_html_content(self, file_path: str, html_content: str)` Method

[[Action.update_html_content]]

*   **Purpose:** A utility method to write/overwrite HTML content to a specified file path.
*   **Arguments:**
    *   `file_path (str)`: The absolute path to the HTML file.
    *   `html_content (str)`: The HTML string to write.
*   **Returns:**
    *   `dict`: An error dictionary from `handle_error` if an exception occurs. (Implicitly, as `handle_error` returns a dict, but this function itself doesn't explicitly return it unless an error occurs).
*   **Logic:** Opens the file in write mode (`"w"`) with UTF-8 encoding and writes the content. Logs success. Handles exceptions.

### 5.6. `action(self, body: dict, __user__=None, __event_emitter__=None, __event_call__=None)` Async Method

[[Action.action]]

*   **Purpose:** This is the main execution method for the OpenWebUI action. It orchestrates the process of getting user input, querying the LLM, generating HTML, saving it, and updating the chat.
*   **Arguments:**
    *   `body (dict)`: The request payload from OpenWebUI, typically containing messages.
    *   `__user__ (dict, optional)`: A dictionary containing information about the current user (e.g., `id`).
    *   `__event_emitter__ (Callable, optional)`: A function provided by OpenWebUI to send real-time status updates to the client's UI.
    *   `__event_call__ (Callable, optional)`: (Not used in this specific implementation but often part of action signatures).
*   **Returns:**
    *   `Optional[dict]`: The modified `body` dictionary with the embedded HTML file reference, or an error dictionary.
*   **Core Logic:**
    1.  Logs the start of the action.
    2.  **UI Status Update (Start):** If `__event_emitter__` is available, sends an initial status update (e.g., "Analyzing data...").
    3.  Extracts `original_content` from the last message in `body["messages"]`.
    4.  **Initialize LLM Client:** Creates an `OpenAI` client instance using `api_key=self.valves.OPENAI_KEY` and `base_url=self.valves.OPENAI_URL`.
    5.  **LLM Query:** Makes a request to the LLM's chat completions endpoint:
        *   Model: `"gpt-4-turbo"` (hardcoded, could be made configurable via `Valves`).
        *   Messages: A list containing the `SYSTEM_PROMPT_BUILD_CHARTS` and the `USER_PROMPT_GENERATE_HTML` formatted with the `original_content`.
        *   Parameters: `max_tokens=1000`, `temperature=0.7`.
    6.  Extracts the `html_content` from the LLM's response.
    7.  Retrieves `user_id` from the `__user__` object.
    8.  Calls `self.create_or_get_file(user_id, html_content)` to save the HTML and get its `file_id`.
    9.  **Embed HTML Reference:** Modifies the content of the last message in the `body` by appending a special placeholder: `\n\n{{{{HTML_FILE_ID_{file_id}}}}}`. OpenWebUI's frontend will recognize this and render the content of the referenced file.
    10. **UI Status Update (End):** If `__event_emitter__` is available, sends a final status update (e.g., "Chart ready!").
    11. Logs successful completion.
    12. **Error Handling:** The entire method is wrapped in a `try...except` block. If any exception occurs, it calls `handle_error(e, "action", body)`.
    13. Returns the (potentially modified) `body`.

---

## 6. Key Components and Flow for Graphing

*   **Entry Point:** [[Action.action]] (async method)
    *   Receives `body`, `__user__`, `__event_emitter__`.
    *   Uses `__event_emitter__` for [[sin/Initialization/Docs/Open WebUI Docs/Open WebUI tools|Open WebUI tools]] status updates.
    *   Uses [[Action.Valves]] for configuration (e.g., `OPENAI_KEY`, `OPENAI_URL`).
    *   Instantiates `openai.OpenAI` client.
    *   Calls `openai.chat.completions.create()` using:
        *   [[Action.SYSTEM_PROMPT_BUILD_CHARTS]]
        *   [[Action.USER_PROMPT_GENERATE_HTML]]
    *   Calls [[Action.create_or_get_file]] with `user_id` and [[sin/Initialization/Docs/Datasets/8. Datasets|8. Datasets]]-generated `html_content`.
        *   [[Action.create_or_get_file]] uses `open_webui.[[sin/1. Initialization/Docs/Datasets/8. Datasets|8. Datasets]].files.Files.get_files()`.
        *   [[Action.create_or_get_file]] uses `open_webui.[[sin/1. Initialization/Docs/Datasets/8. Datasets|8. Datasets]].files.Files.insert_new_file()`.
        *   [[Action.create_or_get_file]] calls [[Action.update_html_content]] (which performs file I/O with `os`).
        *   [[Action.create_or_get_file]] calls [[handle_error]] on exceptions.
    *   Modifies `body` to include `{{{{HTML_FILE_ID_...}}}}`.
    *   [[Action.action]] calls [[handle_error]] on its own exceptions.
*   **Configuration:** [[Action.Valves]] (Pydantic model) is instantiated in [[Action.__init__]].
*   **Error Handling:** All major operations delegate to [[handle_error]] on exceptions.
*   **Logging:** [[logger]] is used by [[handle_error]] and throughout the `Action` class.
*   **File System Interaction:** Primarily through `[[Action.create_or_get_file]]` and `[[Action.update_html_content]]` interacting with `os` and `open_webui.[[sin/1. Initialization/Docs/Datasets/8. Datasets|8. Datasets]].files.Files`.

This detailed breakdown should be very helpful for your [[sin/Initialization/Tools/MCP Server Tools/Obsidian/Obsidian|Obsidian]] documentation and for an [[sin/Initialization/Docs/Datasets/8. Datasets|8. Datasets]] to understand the script's structure and operations.
```

And here is the complete script:

```python
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
from typing import Optional, Dict, Any, Callable # Added Callable for __event_emitter__
from pydantic import BaseModel, Field
from openai import OpenAI
from fastapi import Request # Imported but not directly used in Action class methods shown
from open_webui.utils.misc import pop_system_message # Imported but not directly used in Action class methods shown
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
        "inputs": inputs, # Be cautious about logging sensitive data from inputs
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
        # Example: Add LLM model choice to Valves
        # LLM_MODEL: str = Field(
        # default="gpt-4-turbo", description="The LLM model to use for chart generation."
        # )


    SYSTEM_PROMPT_BUILD_CHARTS = """
    Objective:
    Your goal is to analyze the user's query, extract relevant data, and generate an appropriate chart.
    
    Steps:
    1. Identify the data provided in the query.
    2. Determine the best chart type (bar, pie, line, scatter, etc.).
    3. Generate clean, well-structured HTML with embedded JavaScript (Plotly).
    4. Ensure the chart scale is properly calibrated for readability.
    5. If no chart can be generated, return a fun HTML message indicating why (e.g., "Not enough data for a chart, but here's a cookie recipe!").

    Constraints:
    - Output **only** HTML (no extra text or markdown, no ```html ... ``` wrappers).
    - Ensure numeric data is properly parsed and formatted.
    - If the data is invalid or insufficient, return a user-friendly HTML error message or an alternative fun HTML response.
    - Make sure the HTML is self-contained and does not rely on external CSS/JS files other than Plotly CDN if needed.
    - The Plotly chart should be responsive if possible.
    """

    USER_PROMPT_GENERATE_HTML = """
    Given this user query: "{Query}", generate the corresponding HTML with an embedded Plotly.js chart.
    If a chart is not possible or appropriate for the query, generate a fun and informative HTML message instead.
    """

    def __init__(self):
        self.valves = self.Valves()
        self.openai: Optional[OpenAI] = None # Type hint for clarity
        # self.html_content = "" # This instance variable appears unused

    def _ensure_openai_client(self):
        """Ensures the OpenAI client is initialized."""
        if not self.openai:
            if not self.valves.OPENAI_KEY:
                logger.error("OPENAI_KEY is not set in Valves.")
                raise ValueError("OpenAI API key is required but not configured.")
            self.openai = OpenAI(
                api_key=self.valves.OPENAI_KEY, base_url=self.valves.OPENAI_URL if self.valves.OPENAI_URL else None
            )

    def update_html_content(self, file_path: str, html_content: str) -> Optional[Dict[str, Any]]:
        """
        Updates or writes new HTML content to a file.

        Args:
            file_path (str): Path to the file.
            html_content (str): The HTML content to write.
        
        Returns:
            Optional[Dict[str, Any]]: An error dictionary if an error occurs, None otherwise.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.debug(f"HTML content saved at: {file_path}")
            return None
        except Exception as e:
            return handle_error(
                e,
                "update_html_content",
                {"file_path": file_path, "html_content_snippet": html_content[:100]}, # Log only a snippet
            )

    def create_or_get_file(self, user_id: str, html_content: str) -> Union[str, Dict[str, Any]]:
        """
        Creates or retrieves an HTML file for visualization.

        Args:
            user_id (str): The ID of the user.
            html_content (str): The generated HTML content.

        Returns:
            Union[str, Dict[str, Any]]: The ID of the stored file, or an error dictionary.
        """
        try:
            # Generate a more unique filename component based on time
            timestamp_filename_part = f"{int(time.time() * 1000)}_{self.valves.html_filename}"
            # The filename stored in the DB should be unique and user-specific for querying
            db_filename_key = f"action_embed/{user_id}/{timestamp_filename_part}" # This is what we'll store and query

            # Define base path for storing files on disk
            # Note: OpenWebUI's Files model might handle the actual storage path differently.
            # This assumes we're managing files in a subdirectory of 'uploads'.
            # Consult OpenWebUI documentation for canonical file storage practices if `Files` handles this.
            disk_storage_directory = os.path.join("uploads", "action_embed", user_id)
            os.makedirs(disk_storage_directory, exist_ok=True)
            disk_file_path = os.path.join(disk_storage_directory, timestamp_filename_part)


            logger.debug(f"Attempting to create/update file. DB key: {db_filename_key}, Disk path: {disk_file_path}")

            # The original script's logic for checking existing files:
            # It iterates all files. This could be very slow.
            # A more direct approach would be to query Files by `db_filename_key` if the model supports it.
            # For now, sticking to the script's provided logic but acknowledging potential inefficiency.
            existing_files = Files.get_files()
            found_file_id = None
            for file_obj in existing_files:
                # The original check `file.filename == f"{directory}/{user_id}/{filename}"` implies that
                # `filename` in the loop is just the base name, not the full `db_filename_key`.
                # Let's assume `file_obj.filename` stores what we defined as `db_filename_key`.
                if file_obj.filename == db_filename_key and file_obj.user_id == user_id:
                    logger.info(f"Existing file found with DB key {db_filename_key}. Updating content.")
                    # We need the actual disk path from file_obj.meta to update, or construct it if not available
                    disk_path_to_update = file_obj.meta.get("path", disk_file_path) # Fallback to newly constructed path
                    
                    error_updating = self.update_html_content(disk_path_to_update, html_content)
                    if error_updating:
                        return error_updating # Propagate error
                    found_file_id = file_obj.id
                    break
            
            if found_file_id:
                return found_file_id

            # Create new file if not found by the loop above
            logger.info(f"Creating new file. DB key: {db_filename_key}, Disk path: {disk_file_path}")
            error_writing = self.update_html_content(disk_file_path, html_content)
            if error_writing:
                return error_writing

            file_id = str(uuid.uuid4())
            file_size = os.path.getsize(disk_file_path)
            meta = {
                "source": "action_generated", # Or some other indicator
                "title": self.valves.html_filename.rsplit('.', 1)[0].replace("_", " ").title(),
                "content_type": "text/html",
                "size": file_size,
                "path": disk_file_path, # Store the actual disk path for reference
            }

            file_data = {
                "id": file_id,
                "filename": db_filename_key, # Use the unique key for DB storage
                "meta": meta,
                "user_id": user_id, # Ensure user_id is part of the data for insert_new_file
                "size": file_size, # Top-level size if required by Files model
            }
            
            # Ensure Files.insert_new_file can handle all these fields or adjust accordingly.
            # The original script's `Files.insert_new_file(user_id, file_data)` might implicitly add user_id.
            new_file = Files.insert_new_file(user_id=user_id, file_data=file_data)
            
            if not new_file or not new_file.id: # Basic check
                raise Exception("Failed to insert new file into database.")

            logger.debug(f"New file created with ID: {new_file.id}")
            return new_file.id

        except Exception as e:
            return handle_error(
                e,
                "create_or_get_file",
                {"user_id": user_id, "html_content_snippet": html_content[:100]},
            )


    async def action(
        self,
        body: dict,
        __user__: Optional[Dict[str, Any]] = None,
        __event_emitter__: Optional[Callable[[Dict[str, Any]], Any]] = None,
        __event_call__: Optional[Callable] = None, # Typically not used for simple actions
    ) -> Optional[dict]:
        """
        Executes the action, generating a chart and embedding it into a response.

        Args:
            body (dict): Request payload.
            __user__ (dict, optional): User metadata.
            __event_emitter__ (Callable, optional): Emits status updates to the UI.
            __event_call__ (Callable, optional): For more complex interactions.

        Returns:
            Optional[dict]: Updated request body with HTML embed tag, or an error dict.
        """
        try:
            logger.info("Action started: Generating visualization")
            self.valves = self.Valves(**body.get("valves", {})) # Load valves from request if provided

            if self.valves.show_status and __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": "Analyzing data for chart...", "done": False}}
                )

            if not body.get("messages") or not isinstance(body["messages"], list) or not body["messages"]:
                raise ValueError("No messages found in the request body.")
            
            original_content = body["messages"][-1].get("content", "")
            if not original_content:
                raise ValueError("Last message has no content.")

            self._ensure_openai_client() # Initialize OpenAI client if not already

            if self.valves.show_status and __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": "Querying LLM for chart HTML...", "done": False}}
                )

            llm_model_to_use = getattr(self.valves, "LLM_MODEL", "gpt-4-turbo") # Example if LLM_MODEL was in Valves

            response = self.openai.chat.completions.create(
                model=llm_model_to_use, # Use configured or default model
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT_BUILD_CHARTS},
                    {
                        "role": "user",
                        "content": self.USER_PROMPT_GENERATE_HTML.format(
                            Query=original_content
                        ),
                    },
                ],
                max_tokens=2048, # Increased for potentially complex HTML
                temperature=0.5, # Slightly lower for more deterministic HTML structure
            )

            html_content = response.choices[0].message.content
            if not html_content:
                raise ValueError("LLM returned empty content for HTML chart.")
            
            # Basic HTML validation (very naive)
            if not ("<html" in html_content.lower() or "<!doctype html" in html_content.lower()):
                logger.warning("LLM response does not look like full HTML. Proceeding, but might cause issues.")
                # Potentially wrap it or ask LLM to fix, for now, we use as is.

            if not __user__ or "id" not in __user__:
                raise ValueError("User ID not available, cannot save file.")
            user_id = __user__["id"]

            if self.valves.show_status and __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": "Saving chart file...", "done": False}}
                )

            file_id_or_error = self.create_or_get_file(user_id, html_content)
            if isinstance(file_id_or_error, dict) and file_id_or_error.get("error"):
                # This is an error dictionary from create_or_get_file
                logger.error(f"Failed to create or get file: {file_id_or_error.get('message')}")
                return file_id_or_error # Return the error to OpenWebUI
            
            file_id = file_id_or_error # It's a string (file_id)

            # Append the embed tag to the last message's content
            body["messages"][-1]["content"] += f"\n\n{{{{HTML_FILE_ID_{file_id}}}}}"
            # Or, if you want to replace or add a new message:
            # body["messages"].append({"role": "assistant", "content": f"Here's your chart: {{{{HTML_FILE_ID_{file_id}}}}}"})

            if self.valves.show_status and __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": "Chart ready!", "done": True}}
                )
            logger.info("Action completed successfully, HTML embed tag added.")
            return body # Return the modified body

        except Exception as e:
            # Log the error and return a structured error message
            error_response = handle_error(e, "action", {"body_messages_count": len(body.get("messages",[]))})
            if self.valves.show_status and __event_emitter__:
                 await __event_emitter__(
                    {"type": "status", "data": {"description": f"Error: {error_response['message']}", "done": True, "error": True}}
                )
            return error_response

# Example of how this might be invoked (conceptual, not runnable without OpenWebUI context)
if __name__ == "__main__":
    # This is a placeholder for testing and cannot fully replicate OpenWebUI environment
    action_instance = Action()

    # Mock __user__ and __event_emitter__
    mock_user = {"id": "test_user_123"}
    
    async def mock_event_emitter(event_data: Dict[str, Any]):
        print(f"EVENT: {event_data}")

    # Sample body
    sample_body = {
        "valves": { # User might override default valves
            "OPENAI_KEY": os.getenv("OPENAI_API_KEY"), # Ensure this is set for testing
            "OPENAI_URL": os.getenv("OPENAI_API_BASE"), # Optional
            "html_filename": "my_custom_chart.html"
        },
        "messages": [
            {"role": "user", "content": "Show me a bar chart of sales: Product A 100, Product B 150, Product C 75"}
        ]
    }

    async def run_test():
        print("Testing Action...")
        if not sample_body["valves"]["OPENAI_KEY"]:
            print("Skipping test: OPENAI_API_KEY environment variable not set.")
            return

        # Ensure 'uploads/action_embed/test_user_123' exists for Files.py to work locally if it writes there
        # This depends on how Files.py is implemented.
        if not os.path.exists("uploads/action_embed/test_user_123"):
             os.makedirs("uploads/action_embed/test_user_123", exist_ok=True)


        result = await action_instance.action(
            body=sample_body,
            __user__=mock_user,
            __event_emitter__=mock_event_emitter
        )
        
        if result and result.get("error"):
            print(f"\nAction failed: {result.get('message')}")
            if result.get("stack_trace"):
                print(f"Stack Trace (snippet):\n{result.get('stack_trace')[:300]}...")
        elif result:
            print("\nAction completed. Modified body:")
            print(json.dumps(result, indent=2))
            # You would then check `uploads/action_embed/test_user_123/` for the HTML file
        else:
            print("\nAction returned None or an unexpected result.")

    import asyncio
    # asyncio.run(run_test())
    print("Example test defined. Set OPENAI_API_KEY and uncomment 'asyncio.run(run_test())' to execute.")
    print("Note: `open_webui.models.Files` behavior in a standalone script might differ from within OpenWebUI.")
```