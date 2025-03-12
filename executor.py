import os
import subprocess
import sys
import shutil

def execute_code(file_path, sandbox_dir):
    """Execute code in a fresh virtual environment after installing requirements with uv."""
    # Define the virtual environment path
    venv_path = os.path.join(sandbox_dir, ".venv")
    
    # Remove existing venv if it exists to ensure a fresh environment
    if os.path.exists(venv_path):
        shutil.rmtree(venv_path)
    
    # Create a new virtual environment with uv
    try:
        subprocess.run(["uv", "venv", venv_path], check=True)
    except subprocess.CalledProcessError as e:
        return "", f"Failed to create virtual environment: {e}"
    
    # Determine the Python executable path based on the platform
    if sys.platform == "win32":
        python_path = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_path = os.path.join(venv_path, "bin", "python")
    
    # Check for and install requirements
    requirements_path = os.path.join(sandbox_dir, "requirements.txt")
    if os.path.exists(requirements_path):
        install_cmd = ["uv", "pip", "install", "-r", requirements_path, "--python", python_path]
        try:
            subprocess.run(install_cmd, check=True)
        except subprocess.CalledProcessError as e:
            return "", f"Failed to install requirements: {e}"
    
    # Execute the code
    try:
        result = subprocess.run([python_path, file_path], capture_output=True, text=True)
        return result.stdout, result.stderr
    except Exception as e:
        return "", str(e)