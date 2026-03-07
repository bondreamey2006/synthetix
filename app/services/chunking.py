from app.utils.helpers import clean_text, split_into_sentences


def _build_sentence_chunks(sentences: list[str], chunk_size: int, overlap_sentences: int) -> list[list[str]]:
    chunks: list[list[str]] = []
    i = 0
    while i < len(sentences):
        current: list[str] = []
        current_len = 0
        j = i
        while j < len(sentences):
            sentence = sentences[j]
            projected = current_len + len(sentence) + (1 if current else 0)
            if projected > chunk_size and current:
                break
            current.append(sentence)
            current_len = projected
            j += 1
        if current:
            chunks.append(current)
        if j >= len(sentences):
            break
        i = max(i + 1, j - overlap_sentences)
    return chunks


def chunk_text(documents, chunk_size=300, chunk_overlap=50, min_chunk_chars=100):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")

    chunks = []
    for doc in documents:
        raw_text = doc["content"]
        metadata = doc["metadata"]
        sentences = split_into_sentences(raw_text)
        if not sentences:
            continue

        sentence_groups = _build_sentence_chunks(sentences, chunk_size=chunk_size, overlap_sentences=chunk_overlap)
        for idx, group in enumerate(sentence_groups):
            chunk_content = clean_text(" ".join(group))
            if len(chunk_content) < min_chunk_chars and len(sentence_groups) > 1:
                continue

            chunks.append(
                {
                    "chunk_text": chunk_content,
                    "metadata": {
                        "document_name": metadata["document_name"],
                        "chunk_id": idx,
                        "sentences": group,
                    },
                }
            )
    return chunks
