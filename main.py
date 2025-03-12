# main.py
import os
import re
from agents import ProductDesignerAgent, SoftwareEngineerAgent
from file_manager import create_sandbox

# Map agent keys to their classes
AGENT_CLASSES = {
    "product_designer": ProductDesignerAgent,
    "software_engineer": SoftwareEngineerAgent
}

# Force Ollama to use CPU mode if chosen (optional)
os.environ["OLLAMA_USE_GPU"] = "0"

def process_agent_interaction(agent, initial_input):
    """Process interaction with an agent, handling <rinf> if present."""
    current_input = initial_input
    while True:
        response = agent.process_input(current_input)
        if response is None:
            print(f"[{agent.key.upper()} ERROR] Failed to respond.")
            return None
        print(f"{agent.key.replace('_', ' ').title()}: {response}")
        if not agent.needs_more_info(response):
            return response
        prompt = agent.extract_rinf_prompt(response)
        if prompt:
            print(f"{agent.key.replace('_', ' ').title()} asks: {prompt}")
            user_response = input("You: ").strip()
            if user_response.lower() == "exit":
                print(f"Exiting {agent.key} phase.")
                return None
            current_input = user_response
        else:
            print(f"[{agent.key.upper()} ERROR] Invalid <rinf> format.")
            return None

def chain_agents(agent_list, initial_input):
    """Chain agents, passing each response to the next."""
    current_input = initial_input
    for agent in agent_list:
        response = process_agent_interaction(agent, current_input)
        if response is None:
            return None
        current_input = response
    return current_input

def main(provider="ollama", agent_keys=["product_designer", "software_engineer"]):
    print("Please describe what you want to build:")
    user_initial_prompt = input().strip()

    if not user_initial_prompt:
        print("[ERROR] You must enter a project description.")
        return

    sandbox_dir = create_sandbox()
    print(f"[INFO] Using sandbox directory: {sandbox_dir}")

    # Instantiate agents based on keys
    agents = []
    for key in agent_keys:
        agent_class = AGENT_CLASSES.get(key)
        if not agent_class:
            print(f"[ERROR] Unknown agent key: {key}")
            return
        agents.append(agent_class(provider=provider, sandbox_dir=sandbox_dir))

    # Chain agents with initial prompt
    final_output = chain_agents(agents, user_initial_prompt)
    if final_output is None:
        return

    # Interactive loop with the last agent
    last_agent = agents[-1]
    print(f"\n{last_agent.key.replace('_', ' ').title()} is now online. Type 'exit' to quit.\n")
    while True:
        try:
            user_input = input("You: ").strip()
            if user_input.lower() == "exit":
                print("Ending chat. Goodbye!")
                break
            response = process_agent_interaction(last_agent, user_input)
            if response is None:
                continue
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
    main(provider=provider, agent_keys=["product_designer","software_engineer"])