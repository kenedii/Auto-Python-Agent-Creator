import os
import asyncio
import sys
import shutil

async def execute_code(file_path, sandbox_dir):
    """Execute code in a fresh virtual environment after installing requirements with uv."""
    venv_path = os.path.join(sandbox_dir, ".venv")
    if os.path.exists(venv_path):
        shutil.rmtree(venv_path)
    
    # Create virtual environment
    try:
        process = await asyncio.create_subprocess_exec(
            "uv", "venv", venv_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            return "", f"Failed to create virtual environment: {stderr.decode()}"
    except Exception as e:
        return "", f"Failed to create virtual environment: {str(e)}"
    
    # Determine Python path
    if sys.platform == "win32":
        python_path = os.path.join(venv_path, "Scripts", "python.exe")
    else:
        python_path = os.path.join(venv_path, "bin", "python")
    
    # Install requirements if present
    requirements_path = os.path.join(sandbox_dir, "requirements.txt")
    if os.path.exists(requirements_path):
        try:
            process = await asyncio.create_subprocess_exec(
                "uv", "pip", "install", "-r", requirements_path, "--python", python_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                return "", f"Failed to install requirements: {stderr.decode()}"
        except Exception as e:
            return "", f"Failed to install requirements: {str(e)}"
    
    # Execute the script
    try:
        process = await asyncio.create_subprocess_exec(
            python_path, file_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        return stdout.decode(), stderr.decode() if stderr else ""
    except Exception as e:
        return "", str(e)