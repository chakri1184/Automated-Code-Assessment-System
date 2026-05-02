import subprocess

def syntax_check(file_path):
    try:
        result = subprocess.run(
            ["gcc", file_path],
            capture_output=True,
            text=True
        )

        errors = result.stderr.count("error")

        if errors == 0:
            return 100
        else:
            score = max(0, 100 - errors * 10)
            return score

    except Exception as e:
        print("Error:", e)
        return 0