import json
import re
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ==============================
# LOAD INTENTS
# ==============================

with open("intents.json") as f:
    data = json.load(f)

corpus     = []
intent_map = []

for intent_obj in data["intents"]:
    for pattern in intent_obj["patterns"]:
        corpus.append(pattern.lower().strip())
        intent_map.append(intent_obj["intent"])

# ==============================
# BUILD TF-IDF VECTORIZER
# ==============================

vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    analyzer="word",
    stop_words=None,
    min_df=1
)
tfidf_matrix = vectorizer.fit_transform(corpus)

# ==============================
# KNOWN COLLEGE-DOMAIN WORDS
# A query with NONE of these words → immediately fallback.
# Keep this list focused on words that are specific to a
# college helpdesk context.
# ==============================

DOMAIN_WORDS = {
    # Institution
    "ekc", "eranad", "college", "campus",
    # University
    "ktu", "apj", "university", "affiliated",
    # Academics
    "course", "branch", "department", "btech", "engineering",
    "cse", "ece", "eee", "mechanical", "civil", "ai",
    "semester", "exam", "internal", "external", "result",
    "grading", "cgpa", "sgpa", "credit", "attendance",
    "activity", "portal", "registration", "marklist",
    # Admission
    "admission", "apply", "keam", "eligibility",
    "seat", "quota", "nri", "lateral", "intake",
    # Finance
    "fee", "fees", "tuition", "scholarship", "loan",
    "egrant", "waiver",
    # Campus facilities
    "hostel", "library", "transport", "bus", "placement",
    "internship", "training", "nss", "fest", "ragging",
    "discipline", "conduct",
    # Contact
    "contact", "phone", "email", "address",
    # Greetings — always valid
    "hi", "hello", "hey", "bye", "goodbye", "thanks", "thank",
}

def is_in_domain(text: str) -> bool:
    """Return True only if at least one domain word appears in the query."""
    for dw in DOMAIN_WORDS:
        if dw in text:
            return True
    return False

# ==============================
# TEXT CLEANING
# ==============================

def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

# ==============================
# KEYWORD OVERRIDE RULES
# IMPORTANT: Use specific multi-word phrases wherever possible.
# Avoid single generic words that could appear in unrelated sentences.
# ==============================

KEYWORD_RULES = [
    # Greetings / farewells
    (["hi", "hello", "hey", "good morning", "good evening", "good afternoon"], "greeting"),
    (["bye", "goodbye", "see you", "thank you", "thanks"], "goodbye"),

    # Finance
    (["fee structure", "tuition fee", "btech fee", "college fee", "hostel fee",
      "management quota fee", "government quota fee", "nri fee",
      "how much is the fee", "total fee"], "fees"),

    # Hostel
    (["hostel", "boys hostel", "girls hostel", "hostel facility",
      "hostel accommodation"], "hostel"),

    # Transport
    (["college bus", "bus route", "transport facility",
      "bus timing", "bus pickup"], "transport"),

    # Library
    (["library", "digital library", "ebooks", "reference books",
      "library timings"], "library"),

    # Placements
    (["placement", "campus recruitment", "top recruiters", "placement cell",
      "placement record", "average package", "job opportunities"], "placements"),

    # Internship
    (["internship", "industrial training", "summer internship",
      "industry exposure"], "internships"),

    # Scholarships
    (["scholarship", "egrant", "financial aid", "fee waiver",
      "minority scholarship", "merit scholarship",
      "education loan"], "scholarships"),

    # Attendance
    (["attendance", "attendance shortage", "minimum attendance",
      "attendance percentage", "attendance rule"], "attendance_rules"),

    # Results
    (["ktu result", "semester result", "revaluation", "marklist",
      "check result", "result website"], "results"),

    # Exams
    (["ktu exam", "semester exam", "internal exam", "external exam",
      "exam schedule", "exam pattern", "exam rules"], "exams"),

    # Activity points
    (["activity points", "activity point", "nss points",
      "how to get activity points", "minimum activity points"], "activity_points"),

    # Portal
    (["ktu portal", "student portal", "student login",
      "online exam registration", "exam registration"], "student_portal"),

    # Anti-ragging
    (["ragging", "anti ragging", "ragging complaint",
      "ragging helpline"], "anti_ragging"),

    # Discipline
    (["discipline policy", "code of conduct", "disciplinary action",
      "student conduct", "college rules", "rules and regulations"], "discipline"),

    # Contact
    (["contact ekc", "college phone", "college email",
      "college address", "admission office contact",
      "how to contact"], "contact"),

    # Courses
    (["courses offered", "btech courses", "engineering branches",
      "departments in ekc", "cse in ekc", "what courses",
      "branches in ekc"], "courses_offered"),

    # Seats
    (["seat structure", "approved seats", "nri seats",
      "government quota seats", "management quota seats",
      "seat matrix", "intake capacity"], "seat_structure"),

    # Eligibility
    (["eligibility criteria", "btech eligibility", "lateral entry",
      "minimum marks for admission", "pcm marks",
      "who can apply"], "eligibility"),

    # Admission
    (["admission process", "how to apply", "keam admission",
      "steps for admission", "how to join ekc",
      "documents required for admission",
      "how to get admission"], "admission_process"),

    # KTU
    (["what is ktu", "about ktu", "ktu university", "ktu full form",
      "ktu affiliation", "apj abdul kalam technological",
      "ktu established"], "ktu_about"),

    # EKC
    (["about ekc", "what is ekc", "ekc college", "eranad knowledge",
      "tell me about ekc", "ekc overview",
      "ekc technical campus"], "about_ekc"),

    # Training
    (["placement training", "soft skill training", "aptitude training",
      "mock interview", "resume training",
      "personality development"], "training_programs"),

    # Campus life
    (["campus life", "student life", "cultural events",
      "technical fest", "student clubs",
      "college events"], "campus_life"),

    # KTU academics
    (["grading system", "cgpa", "sgpa", "credit system",
      "year back", "promotion rules", "ktu regulations",
      "passing marks", "ktu academic rules"], "ktu_academics"),
]

def keyword_match(text: str):
    """Match on specific college-domain phrases only."""
    for keywords, intent in KEYWORD_RULES:
        for kw in keywords:
            if kw in text:
                return intent
    return None

# ==============================
# THRESHOLDS
# ==============================

TFIDF_THRESHOLD = 0.35   # Minimum cosine score to trust a TF-IDF match
VOTE_MIN_SCORE  = 0.25   # Minimum score for the voting fallback to kick in

# ==============================
# INTENT PREDICTION
# ==============================

def predict_intent(text: str) -> str:
    if not text or len(text.strip()) == 0:
        return "fallback"

    cleaned = clean_text(text)

    # ── GATE 1: Domain check ──────────────────────────────────────────────
    # If the query contains zero college-related words, skip all matching
    # and return fallback immediately.
    # "Who is the prime minister of India?" → no domain words → fallback ✅
    if not is_in_domain(cleaned):
        return "fallback"

    # ── GATE 2: Keyword override ──────────────────────────────────────────
    # Fires only on unambiguous, college-specific phrases.
    kw_intent = keyword_match(cleaned)
    if kw_intent:
        return kw_intent

    # ── GATE 3: TF-IDF cosine similarity ─────────────────────────────────
    try:
        query_vec  = vectorizer.transform([cleaned])
        scores     = cosine_similarity(query_vec, tfidf_matrix)[0]

        best_idx   = int(np.argmax(scores))
        best_score = float(scores[best_idx])

        # Strong confident match
        if best_score >= TFIDF_THRESHOLD:
            return intent_map[best_idx]

        # Moderate match — vote among top-3, but only if best clears minimum bar
        if best_score >= VOTE_MIN_SCORE:
            top_indices = np.argsort(scores)[-3:][::-1]
            top_intents = [intent_map[i] for i in top_indices if scores[i] >= VOTE_MIN_SCORE]
            if top_intents:
                return Counter(top_intents).most_common(1)[0][0]

    except Exception as e:
        print(f"[NLP] Prediction error: {e}")

    # ── FALLBACK ──────────────────────────────────────────────────────────
    return "fallback"
