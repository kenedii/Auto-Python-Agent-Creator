# main.py
import os
from agents import Agent
from file_manager import create_sandbox

# Force Ollama to use CPU mode if chosen (optional)
os.environ["OLLAMA_USE_GPU"] = "0"

def chain_agents(agents, initial_input):
    """Process input through a chain of agents, passing each response to the next."""
    current_input = initial_input
    for agent in agents:
        response = agent.process_input(current_input)
        if response:
            print(f"{agent.key.capitalize()} Agent: {response}")
            current_input = response
        else:
            print(f"[{agent.key.upper()} ERROR] Agent failed to respond.")
            return None
    return current_input

def main(provider="ollama", agent_keys=["product_designer", "software_engineer"]):
    print("Please describe what you want to build:")
    user_initial_prompt = input().strip()

    if not user_initial_prompt:
        print("[ERROR] You must enter a project description.")
        return

    sandbox_dir = create_sandbox()
    print(f"[INFO] Using sandbox directory: {sandbox_dir}")

    # Create agents with specified keys, sharing the same sandbox
    agents = [Agent(key, provider=provider, sandbox_dir=sandbox_dir) for key in agent_keys]

    # Process initial prompt through the chain
    print("\nConnecting to agents...")
    chain_agents(agents, user_initial_prompt)

    print("\nAgents are now online. Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() == "exit":
                print("Ending chat. Goodbye!")
                break

            # Process each user input through the chain
            chain_agents(agents, user_input)
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
    agent_keys = ["product_designer", "software_engineer"]
    main(provider=provider, agent_keys=agent_keys)