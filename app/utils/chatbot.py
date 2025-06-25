import os, datetime, random
import openai

_BASIC_RULES = {
    "hello": "Hi there! How can I help you with ANC information today?",
    "hours": "The clinic operates Monday to Friday 8 am – 4 pm.",
    "thanks": "You’re welcome! Anything else?"
}

def offline_response(message: str) -> str:
    """Very small rule-based fallback."""
    msg = message.lower()
    for kw, rsp in _BASIC_RULES.items():
        if kw in msg:
            return rsp
    return "I’m sorry—I don’t have that information offline."

def online_response(message: str) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY")
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"system", "content":
                   "You are ACMS assistant. Only answer antenatal or appointment related questions."},
                  {"role":"user","content": message}],
        timeout=15
    )
    return chat.choices[0].message.content.strip()

def get_response(message: str) -> str:
    """Hybrid: online if key provided; else fallback."""
    if os.getenv("OPENAI_API_KEY"):
        try:
            return online_response(message)
        except Exception:
            pass                 # network/API failure → fallthrough
    return offline_response(message)
