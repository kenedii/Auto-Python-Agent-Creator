import os
import requests
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
import anthropic

load_dotenv("key.env")

OLLAMA_MODEL_NAME = "deepseek-r1:1.5b"
OLLAMA_API_URL = "http://localhost:11434/v1/chat/completions"
OPENAI_MODEL_NAME = "gpt-3.5-turbo"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_MODEL_NAME = "claude-3-opus-20240229"
HF_DEFAULT_MODEL = "Qwen/Qwen-1_8B-Chat"

hf_model = None
hf_tokenizer = None
anthropic_client = None

def send_agent_message(messages, provider="ollama"):
    if provider.lower() == "openai":
        return _send_openai_message(messages)
    elif provider.lower() == "ollama":
        return _send_ollama_message(messages)
    elif provider.lower() == "huggingface":
        return _send_huggingface_message(messages)
    elif provider.lower() == "anthropic":
        return _send_anthropic_message(messages)
    else:
        raise ValueError(f"Unknown provider: {provider}")

def _send_ollama_message(messages):
    headers = {"Content-Type": "application/json"}
    data = {"messages": messages, "model": OLLAMA_MODEL_NAME}
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

def _send_huggingface_message(messages, model_name=HF_DEFAULT_MODEL):
    global hf_model, hf_tokenizer
    if hf_model is None or hf_tokenizer is None:
        print(f"[INFO] Loading Hugging Face model: {model_name}")
        hf_tokenizer = AutoTokenizer.from_pretrained(model_name)
        hf_model = AutoModelForCausalLM.from_pretrained(model_name)
    try:
        input_text = hf_tokenizer.apply_chat_template(messages, tokenize=False)
        input_ids = hf_tokenizer.encode(input_text, return_tensors="pt")
        output_ids = hf_model.generate(input_ids, max_new_tokens=100)
        response = hf_tokenizer.decode(output_ids[0][len(input_ids[0]):], skip_special_tokens=True)
        return {"choices": [{"message": {"content": response}}]}
    except Exception as err:
        print(f"[ERROR] Hugging Face inference error: {err}")
        return None

def _send_anthropic_message(messages):
    global anthropic_client
    if anthropic_client is None:
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY not set in key.env")
        anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    try:
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