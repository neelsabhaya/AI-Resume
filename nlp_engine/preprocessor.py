"""nlp_engine/preprocessor.py

NLP preprocessing using spaCy: tokenization, lemmatization, stopword removal.
"""
import re
import logging
from functools import lru_cache
from typing import List, Dict

logger = logging.getLogger(__name__)

# Lazy-load the spaCy model to avoid slow startup
_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model 'en_core_web_sm' loaded.")
        except OSError:
            logger.error(
                "spaCy model not found. Run: python -m spacy download en_core_web_sm"
            )
            raise
    return _nlp


def clean_text(text: str) -> str:
    """Remove special characters, extra whitespace, and normalize text."""
    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)
    # Remove email addresses
    text = re.sub(r"\S+@\S+", "", text)
    # Remove phone numbers
    text = re.sub(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", "", text)
    # Remove special characters but keep alphanumeric and spaces
    text = re.sub(r"[^a-zA-Z0-9\s\.\,\-\/\+\#]", " ", text)
    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def preprocess(text: str) -> str:
    """
    Full NLP preprocessing pipeline:
    1. Clean text
    2. Lowercase
    3. Tokenize with spaCy
    4. Lemmatize
    5. Remove stopwords and punctuation

    Returns:
        Space-joined lemmatized tokens.
    """
    nlp = _get_nlp()
    cleaned = clean_text(text.lower())
    doc = nlp(cleaned)

    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop
        and not token.is_punct
        and not token.is_space
        and len(token.text) > 1
    ]
    return " ".join(tokens)


def extract_named_entities(text: str) -> Dict[str, List[str]]:
    """
    Extract named entities from text using spaCy NER.

    Returns:
        Dict with entity labels as keys and lists of entity texts as values.
        Useful labels: ORG (companies), DATE (years), GPE (locations), PERSON
    """
    nlp = _get_nlp()
    doc = nlp(text[:10000])  # Limit to avoid memory issues

    entities: Dict[str, List[str]] = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        if ent.text not in entities[ent.label_]:
            entities[ent.label_].append(ent.text)

    return entities


def get_key_phrases(text: str, top_n: int = 20) -> List[str]:
    """
    Extract key noun phrases from text using spaCy noun chunks.
    Useful for identifying important concepts.
    """
    nlp = _get_nlp()
    doc = nlp(text[:10000])
    phrases = [
        chunk.text.lower().strip()
        for chunk in doc.noun_chunks
        if len(chunk.text.split()) <= 4 and len(chunk.text) > 2
    ]
    # Deduplicate while preserving order
    seen = set()
    unique_phrases = []
    for p in phrases:
        if p not in seen:
            seen.add(p)
            unique_phrases.append(p)
    return unique_phrases[:top_n]
