import sqlite3
import random
import json

# ==============================
# IN-MEMORY RESPONSE CACHE
# Loads all responses once at startup — no repeated DB hits
# ==============================

_response_cache: dict[str, list[str]] = {}

def _load_cache():
    global _response_cache
    try:
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT intent, response FROM responses")
        rows = cursor.fetchall()
        conn.close()

        for intent, response in rows:
            if intent not in _response_cache:
                _response_cache[intent] = []
            _response_cache[intent].append(response)

    except Exception as e:
        print(f"[DB] Warning: Could not load response cache — {e}")

# Load once at import time
_load_cache()


def get_response(intent: str) -> str:
    """Return a random response for the given intent from the cache."""
    responses = _response_cache.get(intent)

    if responses:
        return random.choice(responses)

    # Try DB directly as fallback (in case cache missed something)
    try:
        conn = sqlite3.connect("chatbot.db")
        cursor = conn.cursor()
        cursor.execute("SELECT response FROM responses WHERE intent = ?", (intent,))
        results = cursor.fetchall()
        conn.close()

        if results:
            response = random.choice(results)[0]
            # Update cache for future calls
            _response_cache[intent] = [r[0] for r in results]
            return response

    except Exception as e:
        print(f"[DB] Error fetching response for intent '{intent}': {e}")

    return (
        "I'm sorry, I don't have specific information about that right now. "
        "Please contact the college office directly or try rephrasing your question."
    )


def reload_cache():
    """Call this if you update the DB at runtime."""
    _response_cache.clear()
    _load_cache()
