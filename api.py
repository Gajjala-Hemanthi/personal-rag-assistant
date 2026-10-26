import time
from fastapi import FastAPI
from pydantic import BaseModel
import rag
from ask import answer

app = FastAPI(title="Personal RAG Assistant")


class Question(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask")
def ask(body: Question):
    start = time.time()
    text, hits = answer(body.question)
    return {
        "answer": text,
        "sources": [{"file": h["source"], "score": round(h["score"], 2)} for h in hits],
        "latency_seconds": round(time.time() - start, 2),
    }


@app.post("/ingest")
def ingest():
    rag.ingest()
    return {"status": "ingested"}