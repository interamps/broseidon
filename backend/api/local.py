import requests

PORT = 8080

def generate(prompt: str, max_tokens: int = 500, port: int = PORT) -> str:
    resp = requests.post(
        f"http://localhost:{port}/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "reasoning": "off",
        },
        timeout=30,
    )
    return resp.json()["choices"][0]["message"]["content"]