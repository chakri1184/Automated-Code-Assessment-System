from .ast_utils import extract_signature
from difflib import SequenceMatcher
import subprocess
import os

# -------- Test Case Evaluation --------
def test_case_score(executable, test_cases, timeout=5):
    total_weight = 0
    score = 0

    for inp, expected, weight in test_cases:
        total_weight += weight

        try:
            result = subprocess.run(
                executable,
                input=inp,
                text=True,
                capture_output=True,
                timeout=timeout
            )

            if result.stdout.strip() == expected.strip():
                score += weight

        except subprocess.TimeoutExpired:
            pass
        except Exception:
            pass

    return (score / total_weight) * 100 if total_weight else 0



# -------- AST-Based Similarity (Plagiarism Detection) --------
def plagiarism_score(code1, code2):
    """
    Detects logical similarity by comparing AST structural signatures.
    This is resistant to variable renaming and reformatting.
    """
    sig1 = extract_signature(code1)
    sig2 = extract_signature(code2)
    
    if not sig1 or not sig2:
        # Fallback to text similarity if AST fails
        similarity = SequenceMatcher(None, code1, code2).ratio()
    else:
        similarity = SequenceMatcher(None, sig1, sig2).ratio()
        
    originality = (1 - similarity) * 100
    return originality