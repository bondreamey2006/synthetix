import os
from PyPDF2 import PdfReader
import markdown
from app.utils.logging_config import setup_logging

logger = setup_logging()

def extract_text_from_pdf(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page_num, page in enumerate(reader.pages):
            content = page.extract_text()
            if content:
                text += content + "\n"
    except Exception as e:
        logger.error(f"Error reading PDF {file_path}: {e}")
    return text

def load_documents(docs_folder="docs"):
    documents = []
    if not os.path.exists(docs_folder):
        logger.error(f"Folder {docs_folder} does not exist!")
        return documents

    for filename in os.listdir(docs_folder):
        file_path = os.path.join(docs_folder, filename)
        content = ""
        
        if filename.endswith(".pdf"):
            content = extract_text_from_pdf(file_path)
        elif filename.endswith(".txt") or filename.endswith(".md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        
        if content:
            documents.append({
                "content": content,
                "metadata": {"document_name": filename}
            })
            logger.info(f"Loaded: {filename}")
            
    return documents