from functools import lru_cache
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from app.config import settings
from app.utils.helpers import split_claims


@lru_cache(maxsize=1)
def _load_generator():
    tokenizer = AutoTokenizer.from_pretrained(settings.generation_model_name, token=settings.hf_token)
    model = AutoModelForSeq2SeqLM.from_pretrained(settings.generation_model_name, token=settings.hf_token)
    return tokenizer, model


def generate_claims(question, context_chunks) -> list[str]:
    if not context_chunks:
        return []

    tokenizer, model = _load_generator()
    context_text = "\n".join(c["chunk_text"] for c in context_chunks)

    prompt = (
        "You are a document QA system.\n"
        "Rules:\n"
        "1) Use only the provided context.\n"
        "2) If context is insufficient, return exactly: NOT_FOUND\n"
        "3) Output 2 to 4 concise factual claims.\n"
        "4) Each claim must be one full sentence on a new line.\n\n"
        f"Context:\n{context_text[:3200]}\n\n"
        f"Question: {question}\n"
        "Claims:\n"
    )

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    output = model.generate(
        **inputs,
        max_new_tokens=140,
        do_sample=False,
    )
    text = tokenizer.decode(output[0], skip_special_tokens=True).strip()
    if "NOT_FOUND" in text.upper():
        return []

    claims = split_claims(text)
    return claims[:4]
