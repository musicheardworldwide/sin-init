from google.colab import drive, userdata
import os
import requests
import json
import pandas as pd
from webdav3.client import Client as WebDavClient
from fpdf import FPDF
import fitz  # PyMuPDF for PDF text extraction
import shutil

# Step 1: Set Up WebDAV Connection
def setup_webdav_client():
    options = {
        'webdav_hostname': 'https://webdav.hidrive.ionos.com',
        'webdav_login': 'wesmane34',
        'webdav_password': 'Dullownation123!',
        'webdav_root': '/'
    }
    client = WebDavClient(options)
    return client

# Step 2: List Files in WebDAV Folder
def list_files_in_webdav_folder(client, folder_path):
    try:
        files = client.list(folder_path)
        return files
    except Exception as e:
        print(f"Error listing files in WebDAV folder: {e}")
        return []

# Step 3: Download Files from WebDAV
def download_files_from_webdav(client, folder_path, local_folder):
    if not os.path.exists(local_folder):
        os.makedirs(local_folder)
    files = list_files_in_webdav_folder(client, folder_path)
    for file in files:
        if file.endswith('/'):  # Skip directories
            continue
        remote_path = os.path.join(folder_path, file)
        local_path = os.path.join(local_folder, file)
        try:
            client.download(remote_path, local_path)
            print(f"Downloaded: {file}")
        except Exception as e:
            print(f"Error downloading {file}: {e}")

# Step 4: Extract and Organize Information from Files
def extract_and_organize_info(local_folder):
    organized_data = []
    for filename in os.listdir(local_folder):
        file_path = os.path.join(local_folder, filename)
        if filename.endswith('.txt') or filename.endswith('.md') or filename.endswith('.py'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                organized_data.append({"filename": filename, "content": content})
        elif filename.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                content = json.dumps(data, indent=4)  # Convert JSON to a readable string
                organized_data.append({"filename": filename, "content": content})
        elif filename.endswith('.csv'):
            df = pd.read_csv(file_path)
            content = df.to_string(index=False)  # Convert CSV to a readable string
            organized_data.append({"filename": filename, "content": content})
        elif filename.endswith('.pdf'):
            doc = fitz.open(file_path)
            content = ""
            for page in doc:
                content += page.get_text()
            organized_data.append({"filename": filename, "content": content})
        else:
            print(f"Skipping unsupported file type: {filename}")
    return organized_data

# Step 5: Create a Structured PDF
def create_pdf(organized_data, output_pdf_path):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    for item in organized_data:
        pdf.set_font("Arial", 'B', size=14)
        pdf.cell(200, 10, txt=f"File: {item['filename']}", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=item['content'])
        pdf.ln(10)
    
    pdf.output(output_pdf_path)
    print(f"PDF created and saved to: {output_pdf_path}")

# Step 6: Set Up DeepSeek API
DEEPSEEK_API_KEY = userdata.get('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Step 7: Function to Extract Text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Step 8: Function to Generate Q&A Using DeepSeek API
def generate_qa_with_deepseek(text, iteration=10):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    qa_pairs = []
    prompt_prefix = {
        1: "Generate 10 basic factual questions",
        2: "Generate 10 comprehension questions",
        3: "Generate 10 application questions",
        4: "Generate 10 analysis questions",
        5: "Generate 10 evaluation questions",
        6: "Generate 10 creation questions",
        7: "Generate 10 synthesis questions",
        8: "Generate 10 critical thinking questions",
        9: "Generate 10 problem-solving questions",
        10: "Generate 10 decision-making questions"
    }.get(iteration, "Generate 10 questions")
    
    prompt = f"Based on the following text:\n\n{text}\n\n{prompt_prefix} based on Bloom's taxonomy level {iteration}. Generate both questions and answers at the highest level. Ensure the answers are detailed and comprehensive, using up to 7,200 tokens for the response."
    
    data = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 7200
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        qa_response = result['choices'][0]['message']['content']
        qa_pairs.append(qa_response)
    else:
        print(f"Error: {response.status_code}, {response.text}")
    return qa_pairs

# Step 9: Function to Save Q&A to a Structured Text File
def save_to_text_file(qa_pairs, output_text_file):
    with open(output_text_file, 'w', encoding='utf-8') as f:
        for i, qa in enumerate(qa_pairs, 1):
            f.write(f"Q&A Pair {i}:\n")
            f.write(f"{qa}\n")
            f.write("\n")

# Step 10: Function to Save Q&A to a JSON File
def save_to_json_file(qa_pairs, output_json_file):
    data = []
    for qa in qa_pairs:
        if "Question:" in qa and "Answer:" in qa:
            question = qa.split("Question:")[1].split("Answer:")[0].strip()
            answer = qa.split("Answer:")[1].strip()
            data.append({"question": question, "answer": answer})
    with open(output_json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Step 11: Function to Save Q&A to a CSV File
def save_to_csv_file(qa_pairs, output_csv_file):
    data = []
    for qa in qa_pairs:
        if "Question:" in qa and "Answer:" in qa:
            question = qa.split("Question:")[1].split("Answer:")[0].strip()
            answer = qa.split("Answer:")[1].strip()
            data.append({"question": question, "answer": answer})
    df = pd.DataFrame(data)
    df.to_csv(output_csv_file, index=False, encoding='utf-8')

# Step 12: Function to Process a Document with Iterations
def process_document_with_iterations(file_path, num_iterations=10):
    if file_path.endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    print(f"Processing document: {file_path}")
    
    all_qa_pairs = []
    for iteration in range(1, num_iterations + 1):
        print(f"Iteration {iteration}: Generating questions...")
        qa_pairs = generate_qa_with_deepseek(text, iteration)
        all_qa_pairs.extend(qa_pairs)
    
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_text_file = f"/content/drive/MyDrive/omni_training/completed_datasets/{base_name}_qa_all.txt"
    save_to_text_file(all_qa_pairs, output_text_file)
    output_json_file = f"/content/drive/MyDrive/omni_training/completed_datasets/{base_name}_qa_all.json"
    save_to_json_file(all_qa_pairs, output_json_file)
    output_csv_file = f"/content/drive/MyDrive/omni_training/completed_datasets/{base_name}_qa_all.csv"
    save_to_csv_file(all_qa_pairs, output_csv_file)
    print("All iterations completed and data saved.")

# Step 13: Mount Google Drive
drive.mount('/content/drive')

# Step 14: Define Paths
webdav_folder_path = "/public/documentation/openwebui"
local_folder = "/content/local_files"
output_pdf_path = "/content/drive/MyDrive/omni_training/converted_pdf/organized_data.pdf"
converted_pdf_folder = "/content/drive/MyDrive/omni_training/converted_pdf"
used_pdf_folder = "/content/drive/MyDrive/omni_training/used_pdf"
completed_datasets_folder = "/content/drive/MyDrive/omni_training/completed_datasets"

# Step 15: Process WebDAV Folder and Create PDF
client = setup_webdav_client()
download_files_from_webdav(client, webdav_folder_path, local_folder)
organized_data = extract_and_organize_info(local_folder)
create_pdf(organized_data, output_pdf_path)

# Step 16: Process PDFs from Google Drive Folder
for filename in os.listdir(converted_pdf_folder):
    if filename.endswith('.pdf'):
        pdf_path = os.path.join(converted_pdf_folder, filename)
        process_document_with_iterations(pdf_path, num_iterations=10)
        shutil.move(pdf_path, os.path.join(used_pdf_folder, filename))
        print(f"Moved {filename} to 'used_pdf' folder.")