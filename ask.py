import os
import sys
import time
from google import genai
from google.genai import types
from sentence_transformers import CrossEncoder
from rag import search

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=types.HttpOptions(timeout=120000),
)
MODEL = "gemini-flash-lite-latest"
RERANK_MIN = -4.0   # reranker score below this = notes can't answer
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

PROMPT = """You answer questions about Gajja using ONLY the notes below.
Rules:
- If the notes do not contain the answer, say exactly: I don't know based on my notes.
- Otherwise answer in one or two short sentences.
- End with the source file names in square brackets, like [about_me.txt].

NOTES:
{context}

QUESTION: {question}"""


def retrieve(question, fetch=5, keep=3):
    hits = search(question, fetch)
    scores = reranker.predict([(question, h["text"]) for h in hits])
    ranked = sorted(zip(scores, hits), key=lambda x: -x[0])
    if ranked[0][0] < RERANK_MIN:
        return []
    return [h for _, h in ranked[:keep]]


def answer(question):
    hits = retrieve(question)
    if not hits:
        return "I don't know based on my notes.", []
    context = "\n".join(f"({h['source']}) {h['text']}" for h in hits)
    for attempt in range(4):
        try:
            r = client.models.generate_content(
                model=MODEL,
                contents=PROMPT.format(context=context, question=question),
            )
            return r.text.strip(), hits
        except Exception as e:
            print("Busy, retrying...", str(e)[:80])
            time.sleep(4 * (attempt + 1))
    return "Model is busy, try again in a minute.", hits


if __name__ == "__main__":
    q = " ".join(sys.argv[1:])
    text, hits = answer(q)
    print("ANSWER:", text)
    print("USED:", [h["source"] for h in hits])