from .ast_utils import extract_features

def structure_score(teacher_code, student_code):
    teacher_features = extract_features(teacher_code)
    student_features = extract_features(student_code)

    total_score = 0
    num_features = len(teacher_features)

    for key in teacher_features:
        tf = teacher_features[key]
        sf = student_features[key]

        if tf == 0:
            feature_score = 100 if sf == 0 else 0
        else:
            # Score based on how close the student's count is to the teacher's
            feature_score = max(0, min(100, (1 - abs(tf - sf) / tf) * 100))

        total_score += feature_score

    return total_score / num_features if num_features else 0