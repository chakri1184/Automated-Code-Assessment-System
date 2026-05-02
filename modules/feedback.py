def generate_feedback(score1, score2, score3, score4, final_score):
    feedback = []

    # Structure
    if score1 < 60:
        feedback.append("Improve code structure and modularity (use functions properly).")
    else:
        feedback.append("Good code structure.")

    # Syntax
    if score2 < 80:
        feedback.append("Fix syntax errors and ensure correct syntax usage.")
    else:
        feedback.append("Syntax is mostly correct.")

    # Test Cases
    if score3 < 70:
        feedback.append("Your program is failing test cases. Check logic and edge cases.")
    else:
        feedback.append("Good handling of test cases.")

    # Originality
    if score4 < 50:
        feedback.append("High similarity detected. Try to write original code.")
    else:
        feedback.append("Code originality is acceptable.")

    # Final Performance
    if final_score >= 75:
        feedback.append("Overall performance is excellent.")
    elif final_score >= 50:
        feedback.append("Average performance. Needs improvement in some areas.")
    else:
        feedback.append("Poor performance. Focus on fundamentals.")

    return feedback