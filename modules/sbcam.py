import re

def count_features(code):
    return {
        "lines": len([line for line in code.split("\n") if line.strip() != ""]),
        
        # Better function detection
        "functions": len(re.findall(r'\bint\s+\w+\s*\(', code)),
        
        # Loop detection
        "loops": len(re.findall(r'\bfor\b', code)) + len(re.findall(r'\bwhile\b', code)),
        
        # Condition detection
        "conditions": len(re.findall(r'\bif\b', code))
    }


def structure_score(teacher_code, student_code):
    teacher_features = count_features(teacher_code)
    student_features = count_features(student_code)

    total_score = 0
    num_features = len(teacher_features)

    for key in teacher_features:
        tf = teacher_features[key]
        sf = student_features[key]

        if tf == 0:
            feature_score = 100 if sf == 0 else 0
        else:
            feature_score = max(0, min(100, (1 - abs(tf - sf) / tf) * 100))

        total_score += feature_score

    return total_score / num_features if num_features else 0