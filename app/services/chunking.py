def chunk_text(documents, chunk_size=500, chunk_overlap=50):
    chunks = []
    
    for doc in documents:
        text = doc["content"]
        metadata = doc["metadata"]
        
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk_content = text[start:end]
            
            chunks.append({
                "chunk_text": chunk_content,
                "metadata": {
                    "document_name": metadata["document_name"],
                    "start_char": start
                }
            }) # Fixed the bracket here
            
            start += (chunk_size - chunk_overlap)
            
    return chunks