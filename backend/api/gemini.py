import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai

# Load .env from the project root (two levels above backend/api/)
_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")

API_GEMINI = os.getenv("API_GEMINI")


def ask_gemini(prompt: str) -> str:
    """Sends a prompt to Gemini using the configured API key and returns the model response."""
    if not API_GEMINI:
        raise ValueError("API_GEMINI is not set. Please specify it in your .env file.")

    client = genai.Client(api_key=API_GEMINI)

    # Support Google GenAI Interactions API with fallback to models.generate_content
    if hasattr(client, "interactions"):
        interaction = client.interactions.create(
            model="gemini-3.8-flash",
            input=prompt,
        )
        return interaction.output_text or ""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text or ""


# Alias for flexibility
generate_response = ask_gemini
