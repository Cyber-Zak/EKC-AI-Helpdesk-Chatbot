"""Dataset sanity check. Run from repo root:  python check_data.py"""
from collections import defaultdict
from backend.nlp_engine import data, clean_text, keyword_match

seen = defaultdict(set)
print("Patterns per intent:")
for o in data["intents"]:
    print(f"  {o['intent']:<20}{len(o['patterns'])}")
    for p in o["patterns"]:
        seen[clean_text(p)].add(o["intent"])

print("\n1) Same pattern in several intents (ambiguous labels):")
for p, ints in seen.items():
    if len(ints) > 1: print(f"  '{p}' -> {sorted(ints)}")

print("\n2) Pattern label disagrees with keyword rules:")
for o in data["intents"]:
    for p in o["patterns"]:
        k = keyword_match(clean_text(p))
        if k and k != o["intent"]:
            print(f"  '{p}': labelled {o['intent']}, rule says {k}")
total = sum(len(o["patterns"]) for o in data["intents"])
print(f"\nTotal: {len(data['intents'])} intents, {total} patterns")
