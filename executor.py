import subprocess

def execute_code(file_path):
    try:
        result = subprocess.run(["python", file_path], capture_output=True, text=True)
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)