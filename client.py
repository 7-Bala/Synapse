import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CEREBRAS_API_KEY")
BASE_URL = "https://api.cerebras.ai/v1"
MODEL = "gemma-4-31b"

def cerebras_chat(messages, model=MODEL, temperature=0.7, max_tokens=512, stream=False, tools=None, tool_choice=None):
    """
    Send a chat completion request to Cerebras.
    """
    import requests
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = tool_choice or "auto"

    response = requests.post(f"{BASE_URL}/chat/completions", headers=headers, json=payload, stream=stream)
    if not stream:
        response.raise_for_status()
        return response.json()
    return response

def cerebras_chat_openai(messages, model=MODEL, temperature=0.7, max_tokens=512, stream=False, tools=None, tool_choice=None):
    """
    Uses the official OpenAI SDK (pointed at Cerebras base URL).
    Requires: pip install openai
    """
    from openai import OpenAI
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = tool_choice or "auto"

    return client.chat.completions.create(**kwargs)

if __name__ == "__main__":
    # Quick sanity test
    result = cerebras_chat([
        {"role": "user", "content": "Say 'Cerebras Gemma 4 is live!'"}
    ])
    print(result["choices"][0]["message"]["content"])
