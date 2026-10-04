import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# DOMAIN_WORDS and KEYWORD_RULES: move your existing lists, unchanged, into backend/rules.py
try:
    from .rules import DOMAIN_WORDS, KEYWORD_RULES
except ImportError:
    from rules import DOMAIN_WORDS, KEYWORD_RULES

BASE_DIR = Path(__file__).resolve().parent
TFIDF_THRESHOLD = 0.35   # tune with evaluate.py
VOTE_MIN_SCORE = 0.25
OUT_OF_DOMAIN_MIN = 0.55  # stricter bar when the query has no college word


def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return re.sub(r"\s+", " ", text)


def prep(text: str) -> str:
    """Clean + drop English stop words so 'is/there/how' cannot create false matches."""
    return " ".join(w for w in clean_text(text).split() if w not in ENGLISH_STOP_WORDS)


# ---- Load intents (path no longer depends on the working directory) ----
with open(BASE_DIR / "intents.json", encoding="utf-8") as f:
    data = json.load(f)

corpus, intent_map = [], []
for obj in data["intents"]:
    if obj["intent"] == "fallback":      # fallback is handled by thresholds, not by patterns
        continue
    for pattern in obj["patterns"]:
        corpus.append(prep(pattern))   # same preparation as queries
        intent_map.append(obj["intent"])

# ---- Word n-grams + character n-grams (handles typos like "scholarhsip") ----
word_vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
char_vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
W = word_vec.fit_transform(corpus)
C = char_vec.fit_transform(corpus)


def _scores(q: str):
    sw = cosine_similarity(word_vec.transform([q]), W)[0]
    sc = cosine_similarity(char_vec.transform([q]), C)[0]
    return 0.5 * sw + 0.5 * sc


# ---- Whole-word matching (fixes "hi" matching inside "which", "this", "within") ----
def _pattern(words):
    alt = "|".join(re.escape(w) for w in sorted(words, key=len, reverse=True))
    return re.compile(r"\b(?:" + alt + r")(?:e?s)?\b")   # allows plurals


# generic words that must pass the gate ("can you help me", "exit", ...)
EXTRA_DOMAIN_WORDS = {"help", "assist", "assistance", "question", "information", "anyone", "exit", "quit"}
DOMAIN_RE = _pattern(set(DOMAIN_WORDS) | EXTRA_DOMAIN_WORDS)
RULE_RES = [(_pattern([k]), k, intent) for kws, intent in KEYWORD_RULES for k in kws]


def is_in_domain(q: str) -> bool:
    return DOMAIN_RE.search(q) is not None


def keyword_match(q: str):
    """Longest matching phrase wins, so 'placement training' beats 'placement'."""
    best, best_len = None, 0
    for rx, kw, intent in RULE_RES:
        if len(kw) > best_len and rx.search(q):
            best, best_len = intent, len(kw)
    return best


def predict(text: str, mode: str = "hybrid"):
    """Returns (intent, score, stage). mode: 'hybrid' | 'keyword' | 'tfidf' (for ablation)."""
    if not text or not text.strip():
        return "fallback", 0.0, "empty"
    q = clean_text(text)

    # Keyword rules first: they are college-specific, and they must also catch
    # "good morning", "see you" etc. which are not in the domain word list.
    if mode in ("hybrid", "keyword"):
        kw = keyword_match(q)
        if kw:
            return kw, 1.0, "keyword"
        if mode == "keyword":
            return "fallback", 0.0, "no_match"

    in_domain = mode != "hybrid" or is_in_domain(q)
    pq = prep(q)
    if not pq:
        return "fallback", 0.0, "empty"

    scores = _scores(pq)
    best = int(np.argmax(scores))
    s = float(scores[best])

    # No college word in the query: not blocked, but needs much higher similarity
    if not in_domain:
        if s >= OUT_OF_DOMAIN_MIN:
            return intent_map[best], s, "tfidf_strict"
        return "fallback", s, "domain_gate"

    if s >= TFIDF_THRESHOLD:
        return intent_map[best], s, "tfidf"
    if s >= VOTE_MIN_SCORE:
        top = np.argsort(scores)[-3:][::-1]
        votes = [intent_map[i] for i in top if scores[i] >= VOTE_MIN_SCORE]
        if votes:
            return Counter(votes).most_common(1)[0][0], s, "vote"
    return "fallback", s, "threshold"


def predict_intent(text: str) -> str:
    """Drop-in replacement: main.py keeps working unchanged."""
    return predict(text)[0]
