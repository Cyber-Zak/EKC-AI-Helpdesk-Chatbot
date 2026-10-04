"""Run from repo root:  python evaluate.py   (needs tests.csv with columns: query,intent)"""
import csv, time
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from backend.nlp_engine import predict

rows = list(csv.DictReader(open("tests.csv", encoding="utf-8")))
X = [r["query"] for r in rows]
y = [r["intent"] for r in rows]

for mode in ["keyword", "tfidf", "hybrid"]:
    t0 = time.perf_counter()
    preds = [predict(q, mode)[0] for q in X]
    ms = (time.perf_counter() - t0) / len(X) * 1000
    print(f"\n=== {mode.upper()} ===")
    print(f"Accuracy: {accuracy_score(y, preds):.3f} | Macro-F1: {f1_score(y, preds, average='macro', zero_division=0):.3f} | {ms:.2f} ms/query")
    if mode == "hybrid":
        print(classification_report(y, preds, zero_division=0))
        labels = sorted(set(y) | set(preds))
        with open("confusion_matrix.csv", "w", newline="") as f:
            w = csv.writer(f); w.writerow([""] + labels)
            for lab, row in zip(labels, confusion_matrix(y, preds, labels=labels)):
                w.writerow([lab] + list(row))
        for q, t, p in zip(X, y, preds):
            if t != p: print(f"WRONG: '{q}' expected={t} got={p}")
