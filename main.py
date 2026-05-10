from modules.sedm import syntax_check

from modules.sbcam import structure_score

from modules.stcam import test_case_score, plagiarism_score

from modules.feedback import generate_feedback

from testcases import load_data_from_csv

from results.plot import plot_interactive_student_scores

import subprocess

import os

import tempfile

import json

from datetime import datetime
import argparse
import tkinter as tk
from tkinter import filedialog



# ========== CONFIGURATION ==========

RESULTS_OUTPUT_FILE = "results/assessment_results.json"  # Save detailed results



# ========== UTILITY FUNCTIONS ==========

def classify(score):

    """Classify score into categories."""

    if score >= 75:

        return "Good"

    elif score >= 50:

        return "Average"

    else:

        return "Poor"



def compile_code(code, student_id, temp_dir):

    """

    Compile C code to executable.

    

    Returns:

        tuple: (success: bool, executable_path: str, error_msg: str)

    """

    # Create temporary C file

    c_file = os.path.join(temp_dir, f"{student_id}.c")

    exe_file = os.path.join(temp_dir, f"{student_id}.exe")

    

    try:

        with open(c_file, 'w', encoding='utf-8') as f:

            f.write(code)

        

        # Compile

        compile_result = subprocess.run(

            ["gcc", c_file, "-o", exe_file],

            capture_output=True,

            text=True,

            timeout=10

        )

        

        if compile_result.returncode != 0:

            return False, exe_file, compile_result.stderr

        

        return True, exe_file, ""

    

    except Exception as e:

        return False, exe_file, str(e)



def evaluate_student(student_id, student_code, teacher_code, test_cases, temp_dir):

    """

    Evaluate a single student's code against teacher solution and test cases.

    

    Returns:

        dict: Contains all scores and feedback

    """

    result = {

        "student_id": student_id,

        "scores": {},

        "final_score": 0,

        "category": "Unknown",

        "feedback": [],

        "compilation_status": "Unknown",

        "error": None

    }

    

    # -------- Compile student code --------

    success, exe_file, error_msg = compile_code(student_code, student_id, temp_dir)

    

    if not success:

        result["compilation_status"] = "Failed"

        result["error"] = error_msg

        result["feedback"].append(f"Compilation Error: {error_msg[:100]}")

        # Even if compilation fails, evaluate structure and originality

        compilation_error = True

    else:

        result["compilation_status"] = "Success"

        compilation_error = False

    

    try:

        # -------- Calculate scores --------

        # Score 1: Structure (can be evaluated without compilation)

        score1 = structure_score(teacher_code, student_code)

        

        # Score 2: Syntax (can be evaluated without compilation)

        temp_c_file = os.path.join(temp_dir, f"{student_id}_syntax.c")

        with open(temp_c_file, 'w', encoding='utf-8') as f:

            f.write(student_code)

        score2 = syntax_check(temp_c_file)

        

        # Score 3: Test Cases (only if compilation succeeded)

        if compilation_error:

            score3 = 0  # No executable to test

        else:

            score3 = test_case_score([exe_file], test_cases)

        

        # Score 4: Originality (can be evaluated without compilation)

        score4 = plagiarism_score(teacher_code, student_code)

        

        # -------- Final Score --------

        final_score = (0.2 * score1) + (0.4 * score2) + (0.2 * score3) + (0.2 * score4)

        

        # Store scores

        result["scores"]["structure"] = round(score1, 2)

        result["scores"]["syntax"] = round(score2, 2)

        result["scores"]["test_cases"] = round(score3, 2)

        result["scores"]["originality"] = round(score4, 2)

        result["final_score"] = round(final_score, 2)

        result["category"] = classify(final_score)

        

        # -------- Generate Feedback --------

        feedback = generate_feedback(score1, score2, score3, score4, final_score)

        result["feedback"] = feedback

        

        # Add compilation error note if applicable

        if compilation_error:

            result["feedback"].insert(0, " Code failed to compile. Test cases could not be evaluated.")

    

    except Exception as e:

        result["error"] = str(e)

        result["final_score"] = 0

        result["category"] = classify(0)

        result["feedback"].append(f"Evaluation Error: {str(e)[:100]}")

    

    return result



# ========== MAIN EXECUTION ==========

def main():

    print("=" * 60)

    print("  AUTOMATED CODE ASSESSMENT SYSTEM")

    print("=" * 60)

    

    parser = argparse.ArgumentParser(description="Automated Code Assessment System")
    parser.add_argument("--dataset", "-d", help="Path to the dataset CSV file", default=None)
    args = parser.parse_args()
    
    csv_file = args.dataset
    if not csv_file:
        print("\n Please select the dataset CSV file from the file browser...")
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        root.attributes('-topmost', True)  # Bring the dialog to the front
        
        csv_file = filedialog.askopenfilename(
            title="Select Dataset CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        
    if not csv_file:
        print(" Error: No dataset selected. Exiting.")
        return

    # -------- Load data from CSV --------
    print(f"\n Loading data from: {csv_file}")
    
    if not os.path.exists(csv_file):
        print(f" Error: CSV file '{csv_file}' not found!")
        print("Please ensure the CSV file exists at the specified path.")
        return
    
    student_codes, teacher_solution, test_cases = load_data_from_csv(csv_file)

    print(f" Loaded {len(student_codes)} student submissions")
    print(f" Loaded {len(test_cases)} test cases")
    
    # -------- Get teacher solution --------
    if teacher_solution is None:
        print(f" Error: Teacher solution not found in CSV!")
        return
    
    print(f" Loaded teacher solution from CSV")

    if not test_cases:
        print("  No test cases found! Using fallback test cases...")
        from testcases import test_cases as fallback_tests
        test_cases = fallback_tests

    

    # -------- Create temporary directory for compilation --------

    with tempfile.TemporaryDirectory() as temp_dir:

        # Dynamically generate missing expected outputs using the teacher solution
        missing_expected = any(tc[1] is None for tc in test_cases)
        if missing_expected:
            print("\n Generating missing expected outputs using Teacher Solution...")
            success, exe_file, error_msg = compile_code(teacher_solution, "teacher", temp_dir)
            if not success:
                print(f" Error: Failed to compile teacher solution!\n{error_msg}")
                return
                
            updated_test_cases = []
            for inp, expected, weight in test_cases:
                if expected is None:
                    try:
                        result = subprocess.run(
                            exe_file,
                            input=inp,
                            text=True,
                            capture_output=True,
                            timeout=5
                        )
                        expected = result.stdout
                    except Exception as e:
                        print(f" Error running teacher solution for test case: {e}")
                        expected = ""
                updated_test_cases.append((inp, expected, weight))
            test_cases = updated_test_cases

        all_results = {}

        final_scores = {}

        

        print("\n" + "=" * 60)

        print("  EVALUATING SUBMISSIONS")

        print("=" * 60)

        

        # -------- Evaluate each student --------

        for idx, (student_id, student_code) in enumerate(student_codes.items(), 1):

            print(f"\n[{idx}/{len(student_codes)}] Evaluating {student_id}...")

            

            result = evaluate_student(student_id, student_code, teacher_solution, test_cases, temp_dir)

            all_results[student_id] = result

            final_scores[student_id] = result["final_score"]

            

            # Print summary for this student

            print(f"   Compilation : {result['compilation_status']}")

            print(f"   Structure   : {result['scores']['structure']:.2f}%")

            print(f"   Syntax      : {result['scores']['syntax']:.2f}%")

            print(f"   Test Cases  : {result['scores']['test_cases']:.2f}%")

            print(f"   Originality : {result['scores']['originality']:.2f}%")

            print(f"   Final Score : {result['final_score']:.2f}% ({result['category']})")

            

            if result["error"]:

                print(f"     Error: {result['error'][:80]}")

    

    # ========== GENERATE OUTPUT ==========

    print("\n" + "=" * 60)

    print("  ASSESSMENT RESULTS")

    print("=" * 60)

    

    # Sort by final score

    sorted_results = sorted(all_results.items(), key=lambda x: x[1]["final_score"], reverse=True)

    

    # Display results table

    print("\n SCORE SUMMARY:")

    print(f"{'Student':<15} {'Compile':<10} {'Structure':<12} {'Syntax':<10} {'Tests':<10} {'Originality':<12} {'Final':<10} {'Category':<10}")

    print("-" * 110)

    

    for student_id, result in sorted_results:

        compile_status = "" if result["compilation_status"] == "Success" else ""

        print(f"{student_id:<15} {compile_status:<10} {result['scores']['structure']:<12.2f} "

              f"{result['scores']['syntax']:<10.2f} {result['scores']['test_cases']:<10.2f} "

              f"{result['scores']['originality']:<12.2f} {result['final_score']:<10.2f} {result['category']:<10}")

    

    # Statistics

    print("\n STATISTICS:")

    successful = [r for r in all_results.values() if r["compilation_status"] == "Success"]

    failed = [r for r in all_results.values() if r["compilation_status"] == "Failed"]

    

    all_scores = [r["final_score"] for r in all_results.values()]

    

    print(f"   Total Submissions: {len(all_results)}")

    print(f"   Successful Compilations: {len(successful)}")

    print(f"   Failed Compilations: {len(failed)}")

    

    if all_scores:

        print(f"   Average Score (All): {sum(all_scores)/len(all_scores):.2f}%")

        print(f"   Highest Score: {max(all_scores):.2f}%")

        print(f"   Lowest Score: {min(all_scores):.2f}%")

        

        categories = {"Good": 0, "Average": 0, "Poor": 0}

        for r in all_results.values():

            categories[r["category"]] += 1

        print(f"   Good Submissions (75+%): {categories['Good']}")

        print(f"   Average Submissions (50-74%): {categories['Average']}")

        print(f"   Poor Submissions (<50%): {categories['Poor']}")

    

    # Save detailed results to JSON

    os.makedirs(os.path.dirname(RESULTS_OUTPUT_FILE) or ".", exist_ok=True)

    with open(RESULTS_OUTPUT_FILE, 'w', encoding='utf-8') as f:

        all_scores_list = [r["final_score"] for r in all_results.values()]

        json.dump({

            "timestamp": datetime.now().isoformat(),

            "total_submissions": len(all_results),

            "successful_compilations": len(successful),

            "failed_compilations": len(failed),

            "results": all_results,

            "summary": {

                "average_score": sum(all_scores_list) / len(all_scores_list) if all_scores_list else 0,

                "max_score": max(all_scores_list) if all_scores_list else 0,

                "min_score": min(all_scores_list) if all_scores_list else 0

            }

        }, f, indent=2)

    

    print(f"\n Detailed results saved to: {RESULTS_OUTPUT_FILE}")

    

    # ========== VISUALIZATION ==========

    print("\n Generating interactive visualization...")

    

    if final_scores:

        # Main interactive visualization - Final scores with component breakdown on hover

        print("    Creating final scores visualization...")

        plot_interactive_student_scores(all_results)

    

    print("\n" + "=" * 60)

    print("  ASSESSMENT COMPLETE")

    print("=" * 60)



if __name__ == "__main__":

    main()