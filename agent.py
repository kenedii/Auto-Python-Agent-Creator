import os
import requests
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
import anthropic

# Load environment variables from key.env
load_dotenv("key.env")

# Configuration for each provider
# Ollama
OLLAMA_MODEL_NAME = "deepseek-r1:1.5b"
OLLAMA_API_URL = "http://localhost:11434/v1/chat/completions"
# OpenAI
OPENAI_MODEL_NAME = "gpt-3.5-turbo"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL_NAME = "claude-3-opus-20240229"
# HuggingFace
HF_DEFAULT_MODEL = "Qwen/Qwen-1_8B-Chat"
# DeepSeek
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL_NAME = "deepseek-chat"  
DEEPSEEK_API_URL = "https://api.deepseek.com"

# Global variables for Hugging Face model and tokenizer
hf_model = None
hf_tokenizer = None

# Global variable for Anthropic client
anthropic_client = None

def send_agent_message(messages, provider="ollama", max_tokens=16000):
    """Send a message to the specified provider and return the response."""
    if provider.lower() == "openai":
        return _send_openai_message(messages, max_tokens)
    elif provider.lower() == "ollama":
        return _send_ollama_message(messages)
    elif provider.lower() == "huggingface":
        return _send_huggingface_message(messages)
    elif provider.lower() == "anthropic":
        return _send_anthropic_message(messages)
    elif provider.lower() == "deepseek":
        return _send_deepseek_message(messages)
    else:
        raise ValueError(f"Unknown provider: {provider}")

def _send_ollama_message(messages):
    """Send messages to the Ollama API."""
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

def _send_openai_message(messages, max_tokens):
    """Send messages to the OpenAI API."""
    import openai
    openai.api_key = OPENAI_API_KEY
    
    # Approximate token count: 1 token ≈ 4 characters
    total_chars = sum(len(m["content"]) for m in messages)
    max_chars = (max_tokens - 1000) * 4  # Reserve 1,000 tokens for the response
    
    if total_chars > max_chars:
        # Preserve system message, remove oldest non-system messages
        system_message = next((m for m in messages if m["role"] == "system"), None)
        other_messages = [m for m in messages if m["role"] != "system"]
        while total_chars > max_chars and other_messages:
            removed = other_messages.pop(0)
            total_chars -= len(removed["content"])
        messages = [system_message] + other_messages if system_message else other_messages
    
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL_NAME,
            messages=messages
        )
        return response
    except Exception as err:
        print(f"[ERROR] OpenAI error: {err}")
        return None

def _send_huggingface_message(messages, model_name=HF_DEFAULT_MODEL):
    """Send messages to a Hugging Face model for local inference."""
    global hf_model, hf_tokenizer
    if hf_model is None or hf_tokenizer is None:
        print(f"[INFO] Loading Hugging Face model: {model_name}")
        hf_tokenizer = AutoTokenizer.from_pretrained(model_name)
        hf_model = AutoModelForCausalLM.from_pretrained(model_name)
    
    try:
        # Format messages using the chat template
        input_text = hf_tokenizer.apply_chat_template(messages, tokenize=False)
        input_ids = hf_tokenizer.encode(input_text, return_tensors="pt")
        output_ids = hf_model.generate(input_ids, max_new_tokens=100)
        response = hf_tokenizer.decode(output_ids[0][len(input_ids[0]):], skip_special_tokens=True)
        # Return in a format compatible with other providers
        return {"choices": [{"message": {"content": response}}]}
    except Exception as err:
        print(f"[ERROR] Hugging Face inference error: {err}")
        return None

def _send_anthropic_message(messages):
    """Send messages to the Anthropic API."""
    global anthropic_client
    if anthropic_client is None:
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in key.env")
        anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    try:
        # Separate system message if present
        system_message = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]
        response = anthropic_client.messages.create(
            model=ANTHROPIC_MODEL_NAME,
            messages=user_messages,
            system=system_message,
            max_tokens=100
        )
        return {"choices": [{"message": {"content": response.content[0].text}}]}
    except Exception as err:
        print(f"[ERROR] Anthropic API error: {err}")
        return None

def _send_deepseek_message(messages):
    """Send messages to the DeepSeek API using OpenAI SDK."""
    from openai import OpenAI
    if not DEEPSEEK_API_KEY:
        raise ValueError("DEEPSEEK_API_KEY not set in key.env")
    
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)
    try:
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL_NAME,
            messages=messages,
            stream=False
        )
        return response
    except Exception as err:
        print(f"[ERROR] DeepSeek API error: {err}")
        return None