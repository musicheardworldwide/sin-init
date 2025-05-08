import requests
import os
import json
from tkinter import Tk
from tkinter.filedialog import askdirectory

def call_ollama(messages, tools):
    """Call Ollama API with messages and tools."""
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama323",  # Or your preferred model
        "messages": messages,
        "stream": True,
        "tools": tools
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama API: {e}")
        return None

def process_directory(directory):
    """Processes a directory, extracts files, and prompts the LLM."""

    all_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append(full_path)

    # Create a new directory for extracted files
    extracted_dir = os.path.join(directory, "extracted_files")
    os.makedirs(extracted_dir, exist_ok=True)

    for file_path in all_files:
        try:
            new_path = os.path.join(extracted_dir, os.path.basename(file_path))
            os.rename(file_path, new_path) # Move instead of copy for efficiency
        except Exception as e:
            print(f"Error moving file {file_path}: {e}")
            return None

    dataset = []

    for file_path in os.listdir(extracted_dir):
        if os.path.isfile(os.path.join(extracted_dir, file_path)): # Ensure it's a file
            try:
                with open(os.path.join(extracted_dir, file_path), "r", encoding="utf-8") as f: # Handle encoding
                    file_content = f.read()

                messages = [
                    {"role": "user", "content": f"Analyze the following file content:\n\n{file_content}\n\nAnswer these three questions:\n1. What is the main topic of this file?\n2. What are the key arguments or points made?\n3. What is the overall sentiment or tone of this file?"}
                ]

                response = call_ollama(messages, [])  # No tools needed for this part
                if response and 'choices' in response and len(response['choices']) > 0 and 'message' in response['choices'][0] and 'content' in response['choices'][0]['message']:
                    llm_response = response['choices'][0]['message']['content']
                    answers = llm_response.split('\n') # Simple split - improve parsing as needed

                    dataset.append({
                        "filename": file_path,
                        "question1": answers[0].split(":")[1].strip() if len(answers) > 0 and ":" in answers[0] else "N/A",
                        "question2": answers[1].split(":")[1].strip() if len(answers) > 1 and ":" in answers[1] else "N/A",
                        "question3": answers[2].split(":")[1].strip() if len(answers) > 2 and ":" in answers[2] else "N/A"
                    })
                else:
                    print(f"Error getting response from LLM for {file_path}")
                    dataset.append({
                        "filename": file_path,
                        "question1": "N/A",
                        "question2": "N/A",
                        "question3": "N/A"
                    })
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                dataset.append({
                    "filename": file_path,
                    "question1": "N/A",
                    "question2": "N/A",
                    "question3": "N/A"
                })

    # Save the dataset to a JSON file
    dataset_path = os.path.join(directory, "dataset.json")
    with open(dataset_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=4)

    return dataset_path



if __name__ == "__main__":
    root = Tk()  # Create a root window for the file dialog
    root.withdraw()  # Hide the main window

    selected_directory = askdirectory()  # Open the directory selection dialog

    if selected_directory:
        print(f"Selected directory: {selected_directory}")
        dataset_path = process_directory(selected_directory)
        if dataset_path:
            print(f"Dataset saved to: {dataset_path}")
        else:
            print("Processing failed.")
    else:
        print("No directory selected.")