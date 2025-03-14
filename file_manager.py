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
            
            # Build execution summary
            if error:
                # Only include error, with a snippet of output for context
                output_lines = output.splitlines()
                snippet = "\n".join(output_lines[-10:]) if output_lines else ""
                result_str = f"Execution of {file_path} failed with error: {error}"
                if snippet:
                    result_str += f"\nLast 10 lines of output:\n{snippet}"
            else:
                # Success case: include a snippet of output
                output_lines = output.splitlines()
                snippet = "\n".join(output_lines[-10:]) if output_lines else ""
                result_str = f"Execution of {file_path} succeeded. Last 10 lines of output:\n{snippet}"
            
            # Enforce a character limit
            MAX_SUMMARY_CHARS = 5000
            if len(result_str) > MAX_SUMMARY_CHARS:
                result_str = result_str[:MAX_SUMMARY_CHARS] + "\n... (truncated)"
            
            execution_results.append(result_str)
        except Exception as e:
            print(f"[ERROR] Could not execute code: {e}")
            execution_results.append(f"Execution of {file_path} failed: {e}")

    for match in re.finditer(r"<rinf>(.*?)</rinf>", agent_message):
        prompt = match.group(1).strip()
        print(f"[INFO] Agent requests more information: {prompt}")

    return execution_results