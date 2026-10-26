from sentence_transformers import CrossEncoder
from rag import search
from eval import TESTS, MIN_SCORE

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def get_hits(q, fetch=5, keep=3):
    hits = search(q, fetch)
    if hits[0]["score"] < MIN_SCORE:   # same refusal gate as before
        return []
    scores = reranker.predict([(q, h["text"]) for h in hits])
    ranked = sorted(zip(scores, hits), key=lambda x: -x[0])
    return [h for _, h in ranked[:keep]]


hit1 = hit3 = ans = ref = unans = 0
for q, kw, can in TESTS:
    hits = get_hits(q)
    if can:
        ans += 1
        t = [h["text"].lower() for h in hits]
        hit1 += bool(t) and kw.lower() in t[0]
        hit3 += any(kw.lower() in x for x in t)
    else:
        unans += 1
        ref += (len(hits) == 0)

print("\nWITH RERANKING (fetch 5, keep 3)")
print(f"hit@1: {hit1}/{ans} = {hit1/ans:.0%}")
print(f"hit@3: {hit3}/{ans} = {hit3/ans:.0%}")
print(f"refusals: {ref}/{unans} = {ref/unans:.0%}")