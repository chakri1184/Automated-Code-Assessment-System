from modules.sedm import syntax_check
from modules.sbcam import structure_score
from modules.stcam import test_case_score, plagiarism_score
from modules.feedback import generate_feedback   # ✅ NEW
from testcases import test_cases
from results.plot import plot_scores
import subprocess
import os

# File paths
teacher_file = "teacher_solution/teacher.c"
student_file = "student_submissions/student1.c"

# -------- Compile student code --------
print("Compiling student code...")

compile_result = subprocess.run(
    ["gcc", student_file, "-o", "student.exe"],
    capture_output=True,
    text=True
)

if compile_result.returncode != 0:
    print("Compilation Failed!")
    print(compile_result.stderr)
    exit()

print("Compilation Successful!\n")

# -------- Read code --------
with open(teacher_file, "r") as f:
    teacher_code = f.read()

with open(student_file, "r") as f:
    student_code = f.read()

# -------- Scores --------
score1 = structure_score(teacher_code, student_code)
score2 = syntax_check(student_file)
score3 = test_case_score(["./student.exe"], test_cases)
score4 = plagiarism_score(teacher_code, student_code)

# -------- Final Score --------
final_score = (0.2 * score1) + (0.4 * score2) + (0.2 * score3) + (0.2 * score4)

# -------- Classification --------
def classify(score):
    if score >= 75:
        return "Good"
    elif score >= 50:
        return "Average"
    else:
        return "Poor"

category = classify(final_score)

# -------- Feedback --------
feedback = generate_feedback(score1, score2, score3, score4, final_score)

# -------- Output --------
print("----- RESULTS -----")
print(f"Structure Score   : {score1:.2f}")
print(f"Syntax Score      : {score2:.2f}")
print(f"Test Case Score   : {score3:.2f}")
print(f"Originality Score : {score4:.2f}")
print(f"\nFinal Score       : {final_score:.2f}")
print(f"Category          : {category}")

# -------- Feedback Output --------
print("\n----- FEEDBACK -----")
for f in feedback:
    print(f"- {f}")

# -------- Graph --------
scores = {
    "Structure": score1,
    "Syntax": score2,
    "TestCases": score3,
    "Originality": score4
}

plot_scores(scores)