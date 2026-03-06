from __future__ import annotations
import re

from app.config import settings
from app.services.embeddings import get_embedding_model
from app.services.retrieval import retrieve_context
from app.utils.helpers import clean_text

NOT_FOUND_MESSAGE = "I could not find this in the provided documents. Can you share the relevant document?"


def _confidence_from_score(score: float) -> str:
    if score >= 0.7:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def _candidate_sentences(context_chunks: list[dict]) -> list[dict]:
    candidates: list[dict] = []
    for chunk in context_chunks:
        sentences = chunk.get("sentences") or [chunk["chunk_text"]]
        for sentence in sentences:
            sentence_text = clean_text(sentence)
            if len(sentence_text) < 20:
                continue
            candidates.append(
                {
                    "document": chunk["document"],
                    "sentence": sentence_text,
                    "retrieval_score": chunk["score"],
                }
            )
    return candidates


def _token_overlap_score(question: str, sentence: str) -> float:
    question_tokens = set(re.findall(r"[a-z0-9]+", question.lower()))
    sentence_tokens = set(re.findall(r"[a-z0-9]+", sentence.lower()))
    if not question_tokens or not sentence_tokens:
        return 0.0

    stopwords = {
        "the", "is", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with",
        "how", "what", "why", "when", "where", "who", "has", "have", "had", "did",
        "does", "do", "can", "could", "would", "should", "it", "this", "that", "as",
    }
    q = {t for t in question_tokens if t not in stopwords}
    s = {t for t in sentence_tokens if t not in stopwords}
    if not q or not s:
        return 0.0

    overlap = len(q & s)
    return overlap / len(q)


def _select_supported_sentences(question: str, context_chunks: list[dict], max_items: int = 3) -> list[dict]:
    candidates = _candidate_sentences(context_chunks)
    if not candidates:
        return []

    model = get_embedding_model()
    question_vec = model.encode([question], convert_to_numpy=True, normalize_embeddings=True)[0]
    sentence_texts = [c["sentence"] for c in candidates]
    sentence_vecs = model.encode(sentence_texts, convert_to_numpy=True, normalize_embeddings=True)
    similarity_scores = question_vec @ sentence_vecs.T

    ranked_items: list[dict] = []
    for idx, evidence in enumerate(candidates):
        semantic_score = max(0.0, min(1.0, float(similarity_scores[idx])))
        retrieval_score = max(0.0, min(1.0, float(evidence["retrieval_score"])))
        keyword_score = _token_overlap_score(question, evidence["sentence"])
        final_score = 0.45 * semantic_score + 0.35 * retrieval_score + 0.20 * keyword_score
        if final_score < settings.min_relevance_score:
            continue
        ranked_items.append(
            {
                "document": evidence["document"],
                "snippet": evidence["sentence"],
                "score": round(max(0.0, min(1.0, final_score)), 4),
            }
        )

    ranked = sorted(ranked_items, key=lambda item: item["score"], reverse=True)
    selected: list[dict] = []
    seen_sentences: set[str] = set()
    for item in ranked:
        sentence = clean_text(item["snippet"])
        key = sentence.lower()
        if key in seen_sentences:
            continue
        seen_sentences.add(key)
        selected.append(
            {
                "document": item["document"],
                "snippet": sentence,
                "full_snippet": sentence,
                "score": round(float(item["score"]), 4),
            }
        )
        if len(selected) >= max_items:
            break
    return selected


def run_rag_pipeline(question, namespace: str | None = None):
    context_chunks = retrieve_context(question, k=settings.retrieval_top_k, namespace=namespace)
    if not context_chunks:
        return {"answer": NOT_FOUND_MESSAGE, "sources": [], "confidence": "low", "score": 0.0}

    max_retrieval_score = max(c["score"] for c in context_chunks)
    if max_retrieval_score < settings.min_relevance_score:
        return {"answer": NOT_FOUND_MESSAGE, "sources": [], "confidence": "low", "score": round(max_retrieval_score, 4)}

    top_sources = _select_supported_sentences(question, context_chunks, max_items=3)
    if not top_sources:
        return {"answer": NOT_FOUND_MESSAGE, "sources": [], "confidence": "low", "score": round(max_retrieval_score, 4)}

    top_answer_source = top_sources[0]
    answer_score = float(top_answer_source["score"])
    if answer_score < settings.min_answer_score:
        return {"answer": NOT_FOUND_MESSAGE, "sources": [], "confidence": "low", "score": round(answer_score, 4)}

    answer = clean_text(top_answer_source.get("full_snippet") or top_answer_source.get("snippet", "")).strip()
    if not answer:
        return {"answer": NOT_FOUND_MESSAGE, "sources": [], "confidence": "low", "score": round(max_retrieval_score, 4)}

    # Overall score reflects the average quality of returned evidence, not only the single best match.
    scores = [float(source["score"]) for source in top_sources]
    overall_score = sum(scores) / len(scores)
    confidence = _confidence_from_score(overall_score)
    formatted_sources = [
        {"document": source["document"], "snippet": source["snippet"], "score": source["score"]}
        for source in top_sources
    ]

    return {
        "answer": answer,
        "sources": formatted_sources,
        "confidence": confidence,
        "score": round(float(overall_score), 4),
    }
