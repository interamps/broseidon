"""
api/gemini.py — Gemini client with tool-call loop and in-memory conversation history.

Tool discovery:
    Every .py module inside tools/ that exposes public callable functions is
    auto-registered as a tool.  No manual wiring needed when adding new tool files.

Memory:
    Conversation history is maintained as a list[types.Content] in Python memory.
    NO SQL is used for conversation history — hard exclusion.
"""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Callable

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_ROOT / ".env")

API_GEMINI = os.getenv("API_GEMINI")
MODEL = "gemini-3.8-flash"

log = logging.getLogger(__name__)

# Module-level client singleton — created once, reused every call
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not API_GEMINI:
            raise ValueError("API_GEMINI is not set. Please add it to your .env file.")
        _client = genai.Client(api_key=API_GEMINI)
    return _client

# ---------------------------------------------------------------------------
# Tool auto-discovery
# ---------------------------------------------------------------------------
# Walk every module in the tools/ package and collect public callables.
# Functions starting with _ are skipped (private helpers).

def _discover_tools() -> tuple[list[Callable], dict[str, Callable]]:
    """
    Scan the tools package and return:
      - tools_list : list of Python callables to pass to GenerateContentConfig
      - fn_map     : name → callable, for manual dispatch if needed
    """
    import tools as tools_pkg  # type: ignore

    tools_list: list[Callable] = []
    fn_map: dict[str, Callable] = {}

    for module_info in pkgutil.iter_modules(tools_pkg.__path__):
        module_name = f"tools.{module_info.name}"
        try:
            mod = importlib.import_module(module_name)
        except Exception as e:
            log.warning("Could not import tool module %s: %s", module_name, e)
            continue

        for attr_name, obj in inspect.getmembers(mod, inspect.isfunction):
            if attr_name.startswith("_"):
                continue
            # Only register functions defined in this module (not re-exports)
            if obj.__module__ != module_name:
                continue
            tools_list.append(obj)
            fn_map[attr_name] = obj
            log.debug("Registered tool: %s.%s", module_info.name, attr_name)

    return tools_list, fn_map


# Cache at module level — rediscovered on first call
_TOOLS_LIST: list[Callable] | None = None
_FN_MAP: dict[str, Callable] | None = None


def _get_tools() -> tuple[list[Callable], dict[str, Callable]]:
    global _TOOLS_LIST, _FN_MAP
    if _TOOLS_LIST is None:
        _TOOLS_LIST, _FN_MAP = _discover_tools()
    return _TOOLS_LIST, _FN_MAP


# ---------------------------------------------------------------------------
# Core ask function
# ---------------------------------------------------------------------------

def ask_gemini(
    prompt: str,
    history: list[types.Content] | None = None,
) -> tuple[str, list[types.Content]]:
    """Send *prompt* to Gemini with AFC enabled, and return the final response.

    The SDK's Automatic Function Calling (AFC) handles the tool-call loop
    internally — no manual dispatch loop needed.

    Args:
        prompt:  The user message to send.
        history: Existing conversation history (list of Content objects).
                 Pass the list returned from the previous call to maintain context.
                 NOTE: history is stored purely in Python memory — NO SQL is used.

    Returns:
        A tuple of (response_text, updated_history).
        Thread the returned history into the next call to maintain multi-turn memory.
    """
    client = _get_client()
    tools_list, _ = _get_tools()

    # Build contents from history + new user turn
    # NO SQL — history is a plain Python list in the caller's memory
    history = list(history) if history else []

    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)],
    )
    contents: list[types.Content] = history + [user_content]

    config = types.GenerateContentConfig(
        tools=tools_list,   # auto-discovered
        system_instruction=(
            "You are Broseidon, a helpful and knowledgeable AI assistant. "
            "You have access to database tools for storing and retrieving information. "
            "Be concise, direct, and friendly."
        ),
    )

    # AFC is enabled by default — the SDK drives the tool-call loop automatically
    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=config,
    )

    final_text = response.text or ""

    # Reconstruct full history: original + user turn + all AFC intermediate turns
    # automatic_function_calling_history holds the model/tool turns the SDK executed
    afc_turns: list[types.Content] = getattr(
        response, "automatic_function_calling_history", []
    ) or []

    if afc_turns:
        # AFC history already includes the user turn; skip it to avoid duplication
        updated_history = history + afc_turns
    else:
        # No tool calls — just user turn + model's final response
        model_content = response.candidates[0].content
        updated_history = contents + [model_content]

    return final_text, updated_history


# Alias
generate_response = ask_gemini
