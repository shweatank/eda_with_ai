"""
llm_client.py

Core client setup for calling an LLM API — configured by default for
Google's Gemini free tier, using its OpenAI-compatible endpoint.

Why Gemini instead of Grok: Grok's API is prepaid with no free credits
for new teams. Gemini currently offers a usable free tier via Google AI
Studio with no billing setup required to get started.

Setup:
    pip install openai python-dotenv

    1. Get a free API key from https://aistudio.google.com/apikey
    2. Create a .env file (see .env.example) with:
        GEMINI_API_KEY=your_key_here

Usage:
    from llm_client import ask_llm

    response = ask_llm("Explain how an AND gate works.")
    print(response)

Swapping providers later:
    This client is OpenAI-compatible, so switching to Grok, OpenRouter,
    or OpenAI itself just means changing API_KEY_ENV_VAR, BASE_URL, and
    DEFAULT_MODEL below -- no other code changes needed.
"""

import os
from openai import OpenAI

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is optional -- if not installed, just rely on env vars
    # already being set in the environment.
    pass


# --- Provider configuration ---------------------------------------------
# To switch providers, change these three lines only.

API_KEY_ENV_VAR = "GEMINI_API_KEY"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
DEFAULT_MODEL = "gemini-3.6-flash"  # check ai.google.dev for current free-tier model names

# Other provider examples (uncomment / swap as needed):
# Grok (xAI):     API_KEY_ENV_VAR="XAI_API_KEY",  BASE_URL="https://api.x.ai/v1",             DEFAULT_MODEL="grok-4-fast"
# OpenRouter:     API_KEY_ENV_VAR="OPENROUTER_API_KEY", BASE_URL="https://openrouter.ai/api/v1", DEFAULT_MODEL="<model>:free"
# OpenAI:         API_KEY_ENV_VAR="OPENAI_API_KEY", BASE_URL="https://api.openai.com/v1",      DEFAULT_MODEL="gpt-4o-mini"
# --------------------------------------------------------------------------


API_KEY = os.environ.get(API_KEY_ENV_VAR)

if not API_KEY:
    raise EnvironmentError(
        f"{API_KEY_ENV_VAR} not found. Set it as an environment variable or in a .env file."
    )

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


def ask_llm(
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
) -> str:
    """
    Send a prompt to the configured LLM and return the text response.

    Args:
        prompt: The user message / question.
        system_prompt: Instructions that set the assistant's behavior.
        model: Which model to use.
        temperature: Sampling temperature (0 = deterministic, higher = more varied).

    Returns:
        The model's text response as a string.
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content


def ask_llm_stream(
    prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
):
    """
    Same as ask_llm, but streams the response chunk by chunk.
    Useful for long explanations printed live to the console.

    Yields:
        Text chunks as they arrive.
    """
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


if __name__ == "__main__":
    # quick manual test: python llm_client.py
    print(ask_llm("In one sentence, what is a logic gate?"))