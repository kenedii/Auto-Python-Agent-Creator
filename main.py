# main.py
import os
import re
from agents import Agent
from file_manager import create_sandbox, process_agent_commands
from file_manager import process_agent_commands
from agent import send_agent_message
from system_prompt import PROMPTS

# Force Ollama to use CPU mode if chosen (optional)
os.environ["OLLAMA_USE_GPU"] = "0"

def interact_with_product_designer(agent, initial_input):
    """Interact with the product designer until the response contains no <rinf> tag."""
    current_input = initial_input
    while True:
        response = agent.process_input(current_input)
        if response is None:
            print("[ERROR] Product designer failed to respond.")
            return None
        print(f"Product Designer: {response}")
        if "<rinf>" not in response:
            return response
        # Extract the prompt from <rinf>prompt</rinf>
        match = re.search(r"<rinf>(.*?)</rinf>", response)
        if match:
            prompt = match.group(1)
            print(f"Product Designer asks: {prompt}")
            user_response = input("You: ").strip()
            current_input = user_response
        else:
            print("[ERROR] Invalid <rinf> tag format in product designer's response.")
            return None

def main(provider="ollama", mode="product_software"):
    print("Please describe what you want to build:")
    user_initial_prompt = input().strip()

    if not user_initial_prompt:
        print("[ERROR] You must enter a project description.")
        return

    sandbox_dir = create_sandbox()
    print(f"[INFO] Using sandbox directory: {sandbox_dir}")

    select_mode(user_initial_prompt, sandbox_dir, mode)

def select_mode(user_initial_prompt, sandbox_dir, mode):
    if mode == "product_software":

        # Create agents
        product_designer = Agent("product_designer", provider=provider, sandbox_dir=sandbox_dir)
        software_engineer = Agent("software_engineer", provider=provider, sandbox_dir=sandbox_dir)

        # Interact with product designer until design is final (no <rinf>)
        final_design = interact_with_product_designer(product_designer, user_initial_prompt)
        if final_design is None:
            return

        print("\nFinal design ready. Passing to software engineer...\n")

        # Pass the final design to the software engineer
        software_engineer.process_input(final_design)

        print("\nSoftware Engineer is now online. Type 'exit' to quit.\n")

        # Interaction loop with software engineer
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() == "exit":
                    print("Ending chat. Goodbye!")
                    break
                response = software_engineer.process_input(user_input)
                if response:
                    print(f"Software Engineer: {response}")
                else:
                    print("[ERROR] Software engineer failed to respond.")
            except EOFError:
                print("\n[ERROR] Input interrupted. Exiting gracefully.")
                break
            except KeyboardInterrupt:
                print("\nEnding chat. Goodbye!")
                break
            except Exception as e:
                print(f"[ERROR] An unexpected error occurred: {e}")
                continue
    elif mode == "software":

        messages = [
            {"role": "system", "content": PROMPTS['software_engineer']},
            {"role": "user", "content": user_initial_prompt}
        ]

        print("Connecting to agent...")
        chat_data = send_agent_message(messages, provider=provider)
        if chat_data is None:
            print("[ERROR] Failed to start chat with the agent.")
            return

        assistant_message = chat_data["choices"][0]["message"]
        messages.append(assistant_message)
        print(f"Agent: {assistant_message['content']}")
        execution_results = process_agent_commands(assistant_message, sandbox_dir)
        if execution_results:
            execution_summary = "Execution results:\n" + "\n".join(execution_results)
            messages.append({"role": "system", "content": execution_summary})

        print("\nAgent is now online. Type 'exit' to quit.\n")

        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() == "exit":
                    print("Ending chat. Goodbye!")
                    break

                messages.append({"role": "user", "content": user_input})
                chat_data = send_agent_message(messages, provider=provider)
                if chat_data:
                    assistant_message = chat_data["choices"][0]["message"]
                    messages.append(assistant_message)
                    print(f"Agent: {assistant_message['content']}")
                    execution_results = process_agent_commands(assistant_message, sandbox_dir)
                    if execution_results:
                        execution_summary = "Execution results:\n" + "\n".join(execution_results)
                        messages.append({"role": "system", "content": execution_summary})
                else:
                    print("[ERROR] Failed to get response from agent.")
            except EOFError:
                print("\n[ERROR] Input interrupted. Exiting gracefully.")
                break
            except KeyboardInterrupt:
                print("\nEnding chat. Goodbye!")
                break
            except Exception as e:
                print(f"[ERROR] An unexpected error occurred: {e}")
                continue

if __name__ == "__main__":
    provider = "openai"  # or "ollama"
    main(provider=provider, mode="product_software")