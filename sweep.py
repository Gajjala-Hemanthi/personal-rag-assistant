from rag import search
from eval import TESTS

rows = []
for q, kw, can_answer in TESTS:
    top = search(q, 1)[0]["score"]
    rows.append((q, top, can_answer))
    print(f"{top:.2f}  {'ANSWERABLE  ' if can_answer else 'UNANSWERABLE'}  {q}")

print("\nthreshold | answerable kept | unanswerable refused")
for t in [0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40]:
    a = [r for r in rows if r[2]]
    u = [r for r in rows if not r[2]]
    kept = sum(r[1] >= t for r in a)
    refused = sum(r[1] < t for r in u)
    print(f"  {t:.2f}    |     {kept}/{len(a)}        |     {refused}/{len(u)}")