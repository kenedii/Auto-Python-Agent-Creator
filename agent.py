import os
import requests
from dotenv import load_dotenv

load_dotenv("key.env")

# Configuration for each provider:
OLLAMA_MODEL_NAME = "deepseek-r1:1.5b"
OLLAMA_API_URL = "http://localhost:11434/v1/chat/completions"
OPENAI_MODEL_NAME = "gpt-3.5-turbo"  # for example
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Set this in your environment if using OpenAI

def send_agent_message(messages, provider="ollama"):
    if provider.lower() == "openai":
        return _send_openai_message(messages)
    else:
        return _send_ollama_message(messages)

def _send_ollama_message(messages):
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": messages,
        "model": OLLAMA_MODEL_NAME
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"[ERROR] HTTP Error: {response.text}")
        return None
    except Exception as err:
        print(f"[ERROR] Unexpected error: {err}")
        return None

def _send_openai_message(messages):
    import openai
    openai.api_key = OPENAI_API_KEY
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL_NAME,
            messages=messages
        )
        return response
    except Exception as err:
        print(f"[ERROR] OpenAI error: {err}")
        return None
