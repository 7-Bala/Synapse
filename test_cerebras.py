import os
from dotenv import load_dotenv

load_dotenv()

from client import cerebras_chat, MODEL, API_KEY

def test_simple():
    print("=" * 50)
    print("TEST 1: Simple Completion")
    print("=" * 50)
    result = cerebras_chat([
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain Cerebras inference speed in one sentence."}
    ], max_tokens=100)
    print("✅ Response:", result["choices"][0]["message"]["content"])
    usage = result.get("usage", {})
    time_info = result.get("time_info", {})
    print(f"📊 Tokens: {usage.get('total_tokens')} | Time: {time_info}")
    print()

def test_streaming():
    print("=" * 50)
    print("TEST 2: Streaming")
    print("=" * 50)
    response = cerebras_chat([
        {"role": "user", "content": "Write a haiku about fast AI."}
    ], stream=True, max_tokens=100)
    
    collected = ""
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith("data: "):
                chunk = line[6:]
                if chunk == "[DONE]":
                    break
                try:
                    import json
                    data = json.loads(chunk)
                    content = data["choices"][0]["delta"].get("content", "")
                    collected += content
                    print(content, end="", flush=True)
                except:
                    pass
    print(f"\n✅ Stream complete!\n")

def test_tool_calling():
    print("=" * 50)
    print("TEST 3: Tool Calling")
    print("=" * 50)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get weather in a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    },
                    "required": ["city"]
                }
            }
        }
    ]
    result = cerebras_chat([
        {"role": "user", "content": "What's the weather in San Francisco?"}
    ], tools=tools, max_tokens=100)
    
    msg = result["choices"][0]["message"]
    if msg.get("tool_calls"):
        print(f"🔧 Tool called: {msg['tool_calls'][0]['function']['name']}")
        print(f"🔧 Args: {msg['tool_calls'][0]['function']['arguments']}")
    else:
        print(f"🤖 Direct response: {msg.get('content', 'N/A')}")
    print()

def test_image_input():
    print("=" * 50)
    print("TEST 4: Image Input (base64)")
    print("=" * 50)
    # Replace with a real base64 image string to test
    # Example payload:
    # messages = [
    #     {"role": "user", "content": [
    #         {"type": "text", "text": "Describe this image."},
    #         {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
    #     ]}
    # ]
    print("ℹ️  Uncomment and add a base64 image string to test this.")
    print()

if __name__ == "__main__":
    print(f"API Key present: {'Yes' if API_KEY else 'No'}")
    print(f"Model: {MODEL}\n")
    try:
        test_simple()
        test_streaming()
        test_tool_calling()
        test_image_input()
    except Exception as e:
        print(f"❌ Error: {e}")
