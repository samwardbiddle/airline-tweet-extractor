from difflib import SequenceMatcher

def get_string_similarity(a: str, b: str) -> float:
    """Calculate similarity ratio between two strings."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def match_airline_name(extracted: str, expected: str) -> tuple[bool, float]:
    """
    Match airline names and return both exact match and similarity score.
    Returns (is_exact_match, similarity_percentage)
    """
    if not extracted or not expected:
        return False, 0.0
        
    # Check for exact match first
    is_exact = extracted.strip() == expected.strip()
    
    # Get similarity score
    similarity = get_string_similarity(extracted, expected) * 100
    
    return is_exact, similarity