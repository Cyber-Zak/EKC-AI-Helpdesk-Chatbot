from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from nlp_engine import predict_intent
from database import get_response

app = FastAPI(title="EKC College Chatbot API", version="2.0")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# SCHEMAS
# ==============================

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    intent: str

# ==============================
# ENDPOINTS
# ==============================

@app.get("/")
def root():
    return {"status": "EKC Chatbot is running", "version": "2.0"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    text = req.message.strip()

    if not text:
        return ChatResponse(
            response="Please type a question and I'll be happy to help!",
            intent="fallback"
        )

    intent = predict_intent(text)
    response = get_response(intent)

    return ChatResponse(response=response, intent=intent)


@app.get("/intents")
def list_intents():
    """Dev utility: list all known intents."""
    import json
    with open("intents.json") as f:
        data = json.load(f)
    return {"intents": [i["intent"] for i in data["intents"]]}
