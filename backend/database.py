import logging
import random
import sqlite3
from contextlib import closing
from pathlib import Path

log = logging.getLogger("ekc.db")

DB_PATH = Path(__file__).resolve().parent / "chatbot.db"   # independent of working directory
DEFAULT_REPLY = (
    "I'm sorry, I don't have specific information about that right now. "
    "Please contact the college office directly or try rephrasing your question."
)

_cache: dict[str, list[str]] = {}


def _connect():
    # Read-only: a wrong path now raises an error instead of silently creating an empty DB
    return sqlite3.connect(f"{DB_PATH.as_uri()}?mode=ro", uri=True)


def reload_cache():
    """Load all responses once; call again after editing the DB at runtime."""
    fresh: dict[str, list[str]] = {}
    try:
        with closing(_connect()) as conn:
            for intent, response in conn.execute("SELECT intent, response FROM responses"):
                fresh.setdefault(intent, []).append(response)
    except sqlite3.Error as e:
        log.error("Could not load response cache from %s: %s", DB_PATH, e)
        return
    _cache.clear()
    _cache.update(fresh)
    log.info("Loaded %d intents from database", len(_cache))


def check_consistency(intent_names):
    """Warn if intents.json and the database disagree (a common silent bug)."""
    missing = sorted(set(intent_names) - set(_cache))
    unused = sorted(set(_cache) - set(intent_names))
    if missing:
        log.warning("Intents with NO response in DB (users get the default reply): %s", missing)
    if unused:
        log.warning("DB intents with no patterns in intents.json (unreachable): %s", unused)
    return missing, unused


def get_response(intent: str) -> str:
    responses = _cache.get(intent)
    return random.choice(responses) if responses else DEFAULT_REPLY


reload_cache()

