from rag import search
from eval import TESTS, MIN_SCORE

print("K | hit@K | refusals")
for K in [3, 5, 7]:
    hit = ans = ref = unans = 0
    for q, kw, can in TESTS:
        hits = search(q, K)
        if hits[0]["score"] < MIN_SCORE:
            hits = []
        if can:
            ans += 1
            hit += any(kw.lower() in h["text"].lower() for h in hits)
        else:
            unans += 1
            ref += (len(hits) == 0)
    print(f"{K} | {hit}/{ans} = {hit/ans:.0%} | {ref}/{unans} = {ref/unans:.0%}")