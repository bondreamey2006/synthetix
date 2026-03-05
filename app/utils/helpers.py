def clean_text(text: str) -> str:
    """Removes extra whitespace and newlines for cleaner snippets."""
    return " ".join(text.split())

def format_score(score: float) -> str:
    """Converts a float score to a percentage string."""
    return f"{round(score * 100, 2)}%"