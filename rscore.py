from sentence_transformers import CrossEncoder
from rag import search
from eval import TESTS

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
for q, kw, can in TESTS:
    hits = search(q, 5)
    top = max(reranker.predict([(q, h["text"]) for h in hits]))
    print(f"{top:7.2f}  {'ANSWERABLE  ' if can else 'UNANSWERABLE'}  {q}")