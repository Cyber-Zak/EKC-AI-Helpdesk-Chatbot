import json
import pickle
import numpy as np

from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Dense,
    Embedding,
    LSTM,
    Bidirectional,
    Dropout
)
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# ==============================
# 1️⃣ Load intents
# ==============================
with open("intents.json") as f:
    data = json.load(f)

sentences = []
labels = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        sentences.append(pattern)
        labels.append(intent["intent"])

# ==============================
# 2️⃣ Encode labels
# ==============================
encoder = LabelEncoder()
encoded_labels = encoder.fit_transform(labels)

# ==============================
# 3️⃣ Tokenization
# ==============================
vocab_size = 3000
max_len = 20

tokenizer = Tokenizer(num_words=vocab_size, oov_token="<OOV>")
tokenizer.fit_on_texts(sentences)

sequences = tokenizer.texts_to_sequences(sentences)
padded = pad_sequences(sequences, maxlen=max_len, padding="post")

# Save tokenizer
with open("tokenizer.json", "w") as f:
    f.write(tokenizer.to_json())

# Save label classes
with open("label_encoder.pkl", "wb") as f:
    pickle.dump(encoder.classes_, f)

# ==============================
# 4️⃣ Build LSTM Model
# ==============================
model = Sequential([
    Embedding(vocab_size, 128, input_length=max_len),

    Bidirectional(LSTM(64, return_sequences=True)),
    Dropout(0.3),

    Bidirectional(LSTM(32)),
    Dropout(0.3),

    Dense(64, activation="relu"),
    Dense(len(set(labels)), activation="softmax")
])

model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer="adam",
    metrics=["accuracy"]
)

# ==============================
# 5️⃣ Train
# ==============================
model.fit(
    padded,
    encoded_labels,
    epochs=200,
    batch_size=8,
    verbose=1
)

# ==============================
# 6️⃣ Save Model
# ==============================
model.save("chatbot_model.h5")

print("✅ LSTM model trained and saved successfully.")
