import os
import time
import re
from executor import execute_code

async def create_sandbox():
    timestamp = int(time.time())
    sandbox_dir = f"sandbox_{timestamp}"
    os.makedirs(sandbox_dir, exist_ok=True)
    return sandbox_dir

async def process_agent_commands(assistant_message, sandbox_dir):
    agent_message = assistant_message.get("content", "")
    execution_results = []

    for match in re.finditer(r"<cfol>(.*?)</cfol>", agent_message):
        folder_name = match.group(1).strip()
        try:
            os.makedirs(os.path.join(sandbox_dir, folder_name), exist_ok=True)
            print(f"[INFO] Created folder: {folder_name}")
        except Exception as e:
            print(f"[ERROR] Could not create folder: {e}")

    for match in re.finditer(r"<cfil>(.*?)</cfil>", agent_message):
        file_path = match.group(1).strip()
        try:
            full_path = os.path.join(sandbox_dir, file_path)
            folder = os.path.dirname(full_path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            with open(full_path, "w") as f:
                f.write("# File created by agent\n")
            print(f"[INFO] Created file: {file_path}")
        except Exception as e:
            print(f"[ERROR] Could not create file: {e}")

    for match in re.finditer(r'<efil file="(.*?)">(.*?)</efil>', agent_message, re.DOTALL):
        file_path = match.group(1).strip()
        new_content = match.group(2)
        try:
            full_path = os.path.join(sandbox_dir, file_path)
            folder = os.path.dirname(full_path)
            if folder and not os.path.exists(folder):
                os.makedirs(folder, exist_ok=True)
            with open(full_path, "w") as f:
                f.write(new_content)
            print(f"[INFO] Edited file: {file_path}")
        except Exception as e:
            print(f"[ERROR] Could not edit file: {e}")

    for match in re.finditer(r"<exec>(.*?)</exec>", agent_message):
        file_path = match.group(1).strip()
        try:
            full_path = os.path.join(sandbox_dir, file_path)
            output, error = await execute_code(full_path, sandbox_dir)
            if output:
                print(f"[OUTPUT]\n{output}")
            if error:
                print(f"[ERROR]\n{error}")
            result_str = f"Execution of {file_path}:"
            if output:
                result_str += f" output: {output}"
            if error:
                result_str += f" error: {error}"
            execution_results.append(result_str)
        except Exception as e:
            print(f"[ERROR] Could not execute code: {e}")

    for match in re.finditer(r"<rinf>(.*?)</rinf>", agent_message):
        prompt = match.group(1).strip()
        print(f"[INFO] Agent requests more information: {prompt}")

    return execution_results