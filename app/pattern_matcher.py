# app/pattern_matcher.py

from typing import List, Dict
from app.patterns import FailurePatternLibrary
from app.llm import call_llm
from app.prompts import get_pattern_matcher_prompt
from ollama import Ollama

# Load the failure patterns once
library = FailurePatternLibrary("app/failure_patterns.json")
FAILURE_PATTERNS = library.all()

ollama_client = Ollama()

def pattern_to_text(pattern: Dict) -> str:
    """
    Convert a pattern dict to a text representation for semantic matching.
    """
    return " ".join(
        [pattern["name"]] +
        pattern.get("signals", []) +
        pattern.get("trigger_conditions", []) +
        pattern.get("why_subtle", [])
    )

def match_patterns_semantic(design_text: str, top_k: int = 5) -> List[Dict]:
    """
    Match an RFC, design document, or PR description against failure patterns using Ollama embeddings.
    Returns top_k most relevant patterns.
    """
    # Create corpus for embeddings
    corpus_texts = [pattern_to_text(p) for p in FAILURE_PATTERNS]

    # Request embeddings from Ollama
    embeddings = ollama_client.embeddings(corpus_texts)
    design_embedding = ollama_client.embeddings([design_text])[0]

    # Compute cosine similarity manually
    def cosine(a, b):
        from math import sqrt
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sqrt(sum(x * x for x in a))
        norm_b = sqrt(sum(y * y for y in b))
        return dot / (norm_a * norm_b + 1e-10)

    similarities = [cosine(design_embedding, emb) for emb in embeddings]

    # Rank top_k patterns
    ranked_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:top_k]

    top_patterns = []
    for idx in ranked_indices:
        pattern = FAILURE_PATTERNS[idx].copy()
        pattern["similarity"] = float(similarities[idx])
        top_patterns.append(pattern)

    return top_patterns

def generate_second_opinion(design_text: str) -> str:
    """
    Generate a structured pre-mortem report using pattern matches + LLM.
    """
    matches = match_patterns_semantic(design_text, top_k=5)

    # Build prompt for Ollama
    prompt = get_pattern_matcher_prompt(design_text, matches)

    # Call Ollama LLM
    report = call_llm(prompt)
    return report

# Example usage
if __name__ == "__main__":
    sample_doc = """
    The Notification Dispatcher consumes events from RabbitMQ, applies fanout,
    retries on failure up to 5 times, and stores results in Cassandra. Consumers
    may be slower than producers under peak load. No circuit breakers currently
    implemented.
    """

    report = generate_second_opinion(sample_doc)
    print(report)
