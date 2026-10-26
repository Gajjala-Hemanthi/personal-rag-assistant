from ask import retrieve
from eval import TESTS

# New questions NOT used to pick the threshold. Edit keywords to match your notes.
HELD_OUT = [
    ("which UI toolkit does my Android app use?", "Compose", True),
    ("what did I use to store chat memory in Python?", "JSON", True),
    ("how did I fix the Gemini errors?", "retries", True),
    ("what is my mother's name?", "", False),
    ("which city do I work in?", "", False),
    ("what is my age?", "", False),
]


def evaluate(name, tests):
    h1 = h3 = a = r = u = 0
    for q, kw, can in tests:
        hits = retrieve(q)
        if can:
            a += 1
            t = [h["text"].lower() for h in hits]
            h1 += bool(t) and kw.lower() in t[0]
            ok = any(kw.lower() in x for x in t)
            h3 += ok
            if not ok:
                print("  FAIL:", q)
        else:
            u += 1
            ok = len(hits) == 0
            r += ok
            if not ok:
                print("  FAIL (should refuse):", q)
    print(f"{name}: hit@1 {h1}/{a} = {h1/a:.0%} | hit@3 {h3}/{a} = {h3/a:.0%} | refusals {r}/{u} = {r/u:.0%}")


evaluate("TUNING SET (12)", TESTS)
evaluate("HELD-OUT SET (6)", HELD_OUT)