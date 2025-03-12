import os
from agent import send_agent_message
from file_manager import create_sandbox, process_agent_commands
from system_prompt import SYSTEM_PROMPT

# Force Ollama to use CPU mode if chosen (optional)
os.environ["OLLAMA_USE_GPU"] = "0"

def main(provider="ollama"):
    print("Please describe what you want to build:")
    user_initial_prompt = input().strip()

    if not user_initial_prompt:
        print("[ERROR] You must enter a project description.")
        return

    sandbox_dir = create_sandbox()
    print(f"[INFO] Using sandbox directory: {sandbox_dir}")


    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
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
    process_agent_commands(assistant_message, sandbox_dir)

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
                process_agent_commands(assistant_message, sandbox_dir)
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
    # Set the provider here directly when calling main()
    provider = "openai"   # or "openai"
    main(provider=provider)
