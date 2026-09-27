import json
import requests
from backend.tools import prober

CHAT_PORT = 8080


def call(prompt, max_tokens=500, port=CHAT_PORT):
    resp = requests.post(
        f"http://localhost:{port}/v1/chat/completions",
        json={"messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "reasoning": "off"},
        timeout=30,
    )
    return resp.json()["choices"][0]["message"]["content"]


def _build_tools():
    schemas = prober.to_tool_schemas(prober.scan())
    schemas.append({
        "type": "function",
        "function": {"name": "prober__scan", "description": "List all available tool functions.", "parameters": {"type": "object", "properties": {}}},
    })
    return schemas


def call_with_tools(prompt, max_tokens=500, port=CHAT_PORT, max_steps=4):
    messages = [{"role": "user", "content": prompt}]
    tools = _build_tools()

    for _ in range(max_steps):
        resp = requests.post(
            f"http://localhost:{port}/v1/chat/completions",
            json={"messages": messages, "max_tokens": max_tokens, "tools": tools, "reasoning": "off"},
            timeout=30,
        ).json()
        msg = resp["choices"][0]["message"]
        messages.append(msg)

        if not msg.get("tool_calls"):
            return msg["content"]

        for tc in msg["tool_calls"]:
            fname = tc["function"]["name"]
            args = json.loads(tc["function"]["arguments"] or "{}")

            if fname == "prober__scan":
                result = prober.scan()
            else:
                module, _, fn_name = fname.partition("__")
                try:
                    result = prober.run(module, fn_name, **args)
                except Exception as e:
                    result = {"error": str(e)}

            messages.append({"role": "tool", "tool_call_id": tc["id"], "content": json.dumps(result, default=str)})

    return "max_steps hit — no final answer"


if __name__ == "__main__":
    print("qwen memory test — 'exit' to quit")
    while True:
        try:
            user_input = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue
        print(call_with_tools(user_input))