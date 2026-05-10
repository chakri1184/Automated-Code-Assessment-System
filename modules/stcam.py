import subprocess
import os
import signal
from difflib import SequenceMatcher

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
                timeout=timeout  # Kill process if it runs longer than timeout seconds
            )

            if result.stdout.strip() == expected.strip():
                score += weight

        except subprocess.TimeoutExpired:
            # Student code ran too long (infinite loop). Skip this test case.
            pass
        except Exception:
            pass

    return (score / total_weight) * 100 if total_weight else 0


# -------- Plagiarism Detection --------
def plagiarism_score(code1, code2):
    similarity = SequenceMatcher(None, code1, code2).ratio()
    originality = (1 - similarity) * 100
    return originality