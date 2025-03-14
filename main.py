import os
import asyncio
from agents import ProductDesignerAgent, SoftwareEngineerAgent
from file_manager import create_sandbox

# Map agent keys to their classes
AGENT_CLASSES = {
    "product_designer": ProductDesignerAgent,
    "software_engineer": SoftwareEngineerAgent
}

# Force Ollama to use CPU mode if chosen (optional)
os.environ["OLLAMA_USE_GPU"] = "0"

async def process_agent_interaction(agent, initial_input):
    """Process interaction with an agent, handling <rinf> if present."""
    current_input = initial_input
    while True:
        response = await agent.process_input(current_input)
        if response is None:
            print(f"[{agent.key.upper()} ERROR] Failed to respond.")
            return None
        print(f"{agent.key.replace('_', ' ').title()}: {response}")
        if not agent.needs_more_info(response):
            return response
        prompt = agent.extract_rinf_prompt(response)
        if prompt:
            print(f"{agent.key.replace('_', ' ').title()} asks: {prompt}")
            user_response = input("You: ").strip()  # Synchronous input; see note
            if user_response.lower() == "exit":
                print(f"Exiting {agent.key} phase.")
                return None
            current_input = user_response
        else:
            print(f"[{agent.key.upper()} ERROR] Invalid <rinf> format.")
            return None

async def chain_agents(agent_list, initial_input):
    """Chain agents, passing each response to the next."""
    current_input = initial_input
    for agent in agent_list:
        response = await process_agent_interaction(agent, current_input)
        if response is None:
            return None
        current_input = response
    return current_input

async def main(provider="ollama", agent_keys=["product_designer", "software_engineer"]):
    print("Please describe what you want to build:")
    user_initial_prompt = input().strip()  # Synchronous input

    if not user_initial_prompt:
        print("[ERROR] You must enter a project description.")
        return

    sandbox_dir = await create_sandbox()
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
    final_output = await chain_agents(agents, user_initial_prompt)
    if final_output is None:
        return

    # Retry mechanism to fix execution errors
    last_agent = agents[-1]
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        last_message = last_agent.messages[-1]
        if last_message["role"] == "system" and "error" in last_message["content"].lower():
            fix_prompt = f"The execution failed with the following error:\n{last_message['content']}\nPlease fix the issue and ensure the code runs successfully."
            response = await process_agent_interaction(last_agent, fix_prompt)
            if response is None:
                break
            retry_count += 1
        else:
            break
    if retry_count == max_retries:
        print("[ERROR] Maximum retries reached. Entering interactive mode for manual intervention.")

    # Start interactive post-development session with the last agent
    print(f"\n{last_agent.key.replace('_', ' ').title()} has completed the initial development.")
    print("You can now request additional features or modifications.")
    print("The agent may ask for more information if needed.\n")

    while True:
        # Prompt user for a request
        user_input = input("Your request (or 'exit' to quit): ").strip()  # Synchronous input
        if user_input.lower() == "exit":
            print("Ending chat. Goodbye!")
            break

        # Process the request, which may involve multiple interactions if <rinf> is used
        response = await process_agent_interaction(last_agent, user_input)
        if response is None:
            print("\nRequest aborted or failed. You can try again.")
            continue

        # After a complete response, ask if the user wants more
        continue_chat = input("Did you want anything else? (yes/no): ").strip().lower()
        if continue_chat != "yes":
            print("Ending chat. Goodbye!")
            break

if __name__ == "__main__":
    provider = "openai"  # or "ollama", "anthropic", "huggingface"
    # Run the main function with the specified provider and agent keys
    asyncio.run(main(provider=provider, agent_keys=["software_engineer"]))