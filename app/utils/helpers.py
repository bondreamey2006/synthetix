import re


def clean_text(text: str) -> str:
    """Removes extra whitespace and newlines for cleaner snippets."""
    return " ".join(text.split())


def split_into_sentences(text: str) -> list[str]:
    normalized = text.replace("\r", " ").replace("\n", " ")
    candidates = re.split(r"(?<=[.!?])\s+", normalized)
    sentences = [clean_text(candidate) for candidate in candidates if clean_text(candidate)]
    return sentences


def split_claims(text: str) -> list[str]:
    raw_lines = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
    claims: list[str] = []
    for line in raw_lines:
        chunks = split_into_sentences(line)
        if chunks:
            claims.extend(chunks)
    return claims


def format_score(score: float) -> str:
    """Converts a float score to a percentage string."""
    return f"{round(score * 100, 2)}%"
