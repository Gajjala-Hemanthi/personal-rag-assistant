import sys
import time
from rag import search

MIN_SCORE = 0.22

# (question, keyword that must appear in the retrieved text, answerable?)
TESTS = [
    ("what phone did I test on?", "iQOO", True),
    ("which language is my Android app written in?", "Kotlin", True),
    ("which API does my assistant use?", "Gemini", True),
    ("what is my goal?", "AI engineer", True),
    ("what are my skills?", "Python", True),
    ("what is my name?", "Gajja", True),
    ("what projects have I built?", "Android app", True),
    ("does my app support voice?", "voice", True),
    ("what is my favourite food?", "", False),
    ("which college did I study in?", "", False),
    ("what is my salary?", "", False),
    ("where do I live?", "", False),
]


def get_hits(q):
    # the threshold only decides whether to answer at all (top chunk score);
    # if we answer, we keep all top-3 chunks
    hits = search(q, 3)
    if hits[0]["score"] < MIN_SCORE:
        return []
    return hits


def run(full=False):
    hit1 = hit3 = answerable = refused = unanswerable = correct = 0
    for q, keyword, can_answer in TESTS:
        hits = get_hits(q)
        if can_answer:
            answerable += 1
            texts = [h["text"].lower() for h in hits]
            in1 = bool(texts) and keyword.lower() in texts[0]
            in3 = any(keyword.lower() in t for t in texts)
            hit1 += in1
            hit3 += in3
            print(("PASS" if in3 else "FAIL"), f"hit@1={in1} hit@3={in3} | {q}")
            if full:
                from ask import answer
                text, _ = answer(q)
                ok = keyword.lower() in text.lower()
                correct += ok
                print("     answer:", text, "->", "OK" if ok else "WRONG")
                time.sleep(5)
        else:
            unanswerable += 1
            ok = len(hits) == 0
            refused += ok
            print(("PASS" if ok else "FAIL"), f"refused={ok} | {q}")

    print("\n===== RESULTS =====")
    print(f"Retrieval hit@1: {hit1}/{answerable} = {hit1 / answerable:.0%}")
    print(f"Retrieval hit@3: {hit3}/{answerable} = {hit3 / answerable:.0%}")
    print(f"Correct refusals: {refused}/{unanswerable} = {refused / unanswerable:.0%}")
    if full:
        print(f"Answer accuracy: {correct}/{answerable} = {correct / answerable:.0%}")


if __name__ == "__main__":
    run(full=(len(sys.argv) > 1 and sys.argv[1] == "full"))