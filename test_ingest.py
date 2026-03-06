from app.services.ingestion import build_vector_index

result = build_vector_index()
print(
    f"Ingestion complete. Documents: {result['ingested_documents']}, "
    f"Chunks: {result['generated_chunks']}"
)
