import csv
import json
import random
import re
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, f1_score
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.layers import Bidirectional, Dense, Dropout, Embedding, LSTM
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer

SEED = 42
random.seed(SEED); np.random.seed(SEED); tf.random.set_seed(SEED)   # reproducible

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "artifacts"
OUT.mkdir(exist_ok=True)
VOCAB, MAX_LEN, CONF = 3000, 20, 0.5     # CONF: below this -> "fallback"


def clean_text(t: str) -> str:           # same cleaning as nlp_engine.py
    t = re.sub(r"[^a-z0-9\s]", "", t.lower().strip())
    return re.sub(r"\s+", " ", t)


with open(ROOT / "backend" / "intents.json", encoding="utf-8") as f:
    data = json.load(f)

sentences = [clean_text(p) for o in data["intents"] for p in o["patterns"]]
labels = [o["intent"] for o in data["intents"] for _ in o["patterns"]]

enc = LabelEncoder()
y = enc.fit_transform(labels)
tok = Tokenizer(num_words=VOCAB, oov_token="<OOV>")
tok.fit_on_texts(sentences)
X = pad_sequences(tok.texts_to_sequences(sentences), maxlen=MAX_LEN, padding="post")

# Small data -> small model (the original 2-layer BiLSTM would overfit)
model = Sequential([
    Embedding(VOCAB, 64),
    Bidirectional(LSTM(32)),
    Dropout(0.5),
    Dense(32, activation="relu"),
    Dense(len(enc.classes_), activation="softmax"),
])
model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
model.fit(X, y, epochs=100, batch_size=8, verbose=1,
          callbacks=[EarlyStopping(monitor="loss", patience=10, restore_best_weights=True)])

# Save (JSON instead of pickle: unpickling files is a security risk)
model.save(OUT / "chatbot_lstm.keras")
(OUT / "tokenizer.json").write_text(tok.to_json(), encoding="utf-8")
(OUT / "labels.json").write_text(json.dumps(list(enc.classes_)), encoding="utf-8")


def predict_lstm(texts):
    seq = tok.texts_to_sequences([clean_text(t) for t in texts])
    p = model.predict(pad_sequences(seq, maxlen=MAX_LEN, padding="post"), verbose=0)
    return [enc.classes_[i] if c >= CONF else "fallback" for i, c in zip(p.argmax(1), p.max(1))]


# Honest evaluation on held-out queries, NOT on the training patterns
tests = ROOT / "tests.csv"
if tests.exists():
    rows = list(csv.DictReader(open(tests, encoding="utf-8")))
    Xt, yt = [r["query"] for r in rows], [r["intent"] for r in rows]
    pred = predict_lstm(Xt)
    print(f"\nBiLSTM  Accuracy: {accuracy_score(yt, pred):.3f} | "
          f"Macro-F1: {f1_score(yt, pred, average='macro', zero_division=0):.3f}")
print("Saved model to", OUT)
