# agents.py
import re
from system_prompt import PROMPTS
from agent import send_agent_message  # Placeholder for sending messages to the model
from file_manager import process_agent_commands  # Placeholder for command processing

class Agent:
    def __init__(self, key, provider="ollama", sandbox_dir=None):
        """Initialize an agent with a specific system prompt, provider, and sandbox directory."""
        self.key = key
        self.system_prompt = PROMPTS.get(key, "Default agent prompt")
        self.provider = provider
        self.sandbox_dir = sandbox_dir
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def process_input(self, input_text):
        """Process input text, send it to the agent, handle commands, and return the response."""
        self.messages.append({"role": "user", "content": input_text})
        chat_data = send_agent_message(self.messages, provider=self.provider)
        if chat_data is None:
            print(f"[{self.key.upper()} ERROR] Failed to get response.")
            return None
        assistant_message = chat_data["choices"][0]["message"]
        self.messages.append(assistant_message)
        execution_results = process_agent_commands(assistant_message, self.sandbox_dir)
        if execution_results:
            execution_summary = "Execution results:\n" + "\n".join(execution_results)
            self.messages.append({"role": "system", "content": execution_summary})
        return assistant_message["content"]