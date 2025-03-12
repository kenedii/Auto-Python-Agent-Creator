# Auto-Python-Agent
Functions to easily utilize LLM agents to create python programs and reports.

Instructions:

Specify in if __name__ == "__main__":

provider = "openai"  # or "ollama" configs can be set in agent.py

main(provider=provider, agent_keys=["product_designer", "software_engineer"]) 

make key.env with OPENAI_API_KEY=sk-proj-YoUrKeYh3r3

To create an agent, simply define its system prompt in system_prompt.py dictionary and create an agent with the specified key in agents.py.
