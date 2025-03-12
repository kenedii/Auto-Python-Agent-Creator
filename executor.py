import subprocess

def execute_code(file_path):
    try:
        print(f"[INFO] Executing: {file_path}")
        result = subprocess.run(["python", file_path], capture_output=True, text=True)
        if result.stdout:
            print(f"[OUTPUT]\n{result.stdout}")
        if result.stderr:
            print(f"[ERROR]\n{result.stderr}")
    except Exception as e:
        print(f"[ERROR] Execution failed: {str(e)}")
