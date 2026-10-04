import sqlite3
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:                                   # works as `uvicorn backend.main:app` (root)
    from .nlp_engine import predict, data
    from .database import get_response, check_consistency
except ImportError:                    # and as `uvicorn main:app` (inside backend/)
    from nlp_engine import predict, data
    from database import get_response, check_consistency

check_consistency([i["intent"] for i in data["intents"]])

app = FastAPI(title="EKC College Chatbot API", version="2.1")

# Development: "*". For deployment, replace with your frontend URL(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Query log (for error analysis + user feedback in the paper) ----
LOG_DB = Path(__file__).resolve().parent / "logs.db"

def _init_log():
    with sqlite3.connect(LOG_DB) as c:
        c.execute("""CREATE TABLE IF NOT EXISTS chat_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT DEFAULT CURRENT_TIMESTAMP,
            query TEXT, intent TEXT, score REAL, stage TEXT,
            latency_ms REAL, helpful INTEGER)""")

_init_log()

# ---- Schemas ----
class ChatRequest(BaseModel):
    message: str = Field(..., max_length=500)   # blocks oversized inputs

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float = 0.0
    stage: str = ""
    log_id: int = 0

class Feedback(BaseModel):
    log_id: int
    helpful: bool

# ---- Endpoints ----
@app.get("/")
def root():
    return {"status": "EKC Chatbot is running", "version": "2.1"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    text = req.message.strip()
    if not text:
        return ChatResponse(
            response="Please type a question and I'll be happy to help!",
            intent="fallback")

    t0 = time.perf_counter()
    intent, score, stage = predict(text)
    response = get_response(intent)
    ms = (time.perf_counter() - t0) * 1000

    with sqlite3.connect(LOG_DB) as c:
        cur = c.execute(
            "INSERT INTO chat_log (query, intent, score, stage, latency_ms) VALUES (?,?,?,?,?)",
            (text, intent, score, stage, ms))
        log_id = cur.lastrowid

    return ChatResponse(response=response, intent=intent,
                        confidence=round(score, 3), stage=stage, log_id=log_id)

@app.post("/feedback")
def feedback(fb: Feedback):
    with sqlite3.connect(LOG_DB) as c:
        cur = c.execute("UPDATE chat_log SET helpful=? WHERE id=?", (int(fb.helpful), fb.log_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="log_id not found")
    return {"status": "saved"}

@app.get("/intents")
def list_intents():
    """Dev utility: list all known intents."""
    return {"intents": [i["intent"] for i in data["intents"]]}


# Serve the chat page from the same server: open http://<host>:8000/app/
FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="app")
