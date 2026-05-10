import csv
import os

# Fallback test cases if none found in dataset
test_cases = []

def load_data_from_csv(csv_file):
    """
    Load student codes, teacher solution, and test cases from CSV file.
    Reads positionally:
    Col 0: ID
    Col 1: Code / Input
    Col 2: Expected Output (if any)
    """
    student_codes = {}
    teacher_solution = None
    extracted_test_cases = []
    
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found!")
        return {}, None, []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            
            for row in reader:
                # Skip empty rows
                if not row or not row[0].strip():
                    continue
                    
                row_id = row[0].strip()
                row_id_lower = row_id.lower()
                
                # Skip header rows
                if row_id_lower in ['student_id', 'studentid', 'testcaseid']:
                    continue
                
                # Get Column 1 (Code or Input)
                col1 = row[1].strip() if len(row) > 1 else ""
                
                # Get Column 2 (Expected Output)
                col2 = row[2].strip() if len(row) > 2 else None
                
                # Check for Teacher Solution
                if 'teacher' in row_id_lower:
                    teacher_solution = col1
                
                # Check for Test Cases
                elif 'testcase' in row_id_lower or 'tc' in row_id_lower:
                    # Input is col1, ensure it has a newline for stdin simulation
                    test_input = col1 + '\n'
                    # Default weight is 1
                    extracted_test_cases.append((test_input, col2, 1))
                
                # Otherwise, it's a student submission
                else:
                    if col1:  # Only add if there's actual code
                        student_codes[row_id] = col1
                        
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return {}, None, []
    
    return student_codes, teacher_solution, extracted_test_cases

def get_test_cases_from_csv(csv_file):
    """
    Compatibility function.
    Returns just the test cases parsed by load_data_from_csv.
    """
    _, _, test_cases_list = load_data_from_csv(csv_file)
    return test_cases_list
