import re
from system_prompt import PROMPTS
from agent import send_agent_message
from file_manager import process_agent_commands

class Agent:
    def __init__(self, key, provider="ollama", sandbox_dir=None):
        self.key = key
        self.system_prompt = PROMPTS.get(key, "Default agent prompt")
        self.provider = provider
        self.sandbox_dir = sandbox_dir
        self.messages = [{"role": "system", "content": self.system_prompt}]

    async def process_input(self, input_text):
        """Process input and return the response, handling commands asynchronously."""
        self.messages.append({"role": "user", "content": input_text})
        chat_data = send_agent_message(self.messages, provider=self.provider)  # Assumes sync for now
        if chat_data is None:
            print(f"[{self.key.upper()} ERROR] Failed to get response.")
            return None
        assistant_message = chat_data["choices"][0]["message"]
        self.messages.append(assistant_message)
        execution_results = await process_agent_commands(assistant_message, self.sandbox_dir)
        if execution_results:
            execution_summary = "Execution results:\n" + "\n".join(execution_results)
            self.messages.append({"role": "system", "content": execution_summary})
        return assistant_message["content"]

    def needs_more_info(self, response):
        """Check if the response contains a <rinf> tag."""
        return "<rinf>" in response if response else False

    def extract_rinf_prompt(self, response):
        """Extract the prompt from <rinf> tags."""
        match = re.search(r"<rinf>(.*?)</rinf>", response)
        return match.group(1) if match else None

class ProductDesignerAgent(Agent):
    def __init__(self, provider="ollama", sandbox_dir=None):
        super().__init__("product_designer", provider, sandbox_dir)

    async def process_input(self, input_text):
        """Override to handle product design-specific logic."""
        return await super().process_input(input_text)

class SoftwareEngineerAgent(Agent):
    def __init__(self, provider="ollama", sandbox_dir=None):
        super().__init__("software_engineer", provider, sandbox_dir)

    async def process_input(self, input_text):
        """Override to handle software engineering-specific logic."""
        return await super().process_input(input_text)