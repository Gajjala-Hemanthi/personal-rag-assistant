import os
import sys
import chromadb
from sentence_transformers import SentenceTransformer

DOCS_DIR = "docs"
DB_DIR = "chroma_db"
CHUNK_SIZE = 200     # characters per chunk
OVERLAP = 60         # characters shared between neighbouring chunks

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=DB_DIR)


def chunk_text(text):
    # split into sentences/lines, then group them up to CHUNK_SIZE characters
    pieces = [p.strip() for p in text.replace("\r", "").split("\n") if p.strip()]
    chunks, current = [], ""
    for p in pieces:
        if current and len(current) + len(p) + 1 > CHUNK_SIZE:
            chunks.append(current)
            current = p
        else:
            current = (current + " " + p).strip()
    if current:
        chunks.append(current)
    return chunks


def ingest():
    try:
        client.delete_collection("notes")
    except Exception:
        pass
    col = client.create_collection("notes", metadata={"hnsw:space": "cosine"})
    ids, texts, metas = [], [], []
    for name in os.listdir(DOCS_DIR):
        if not name.endswith((".txt", ".md")):
            continue
        with open(os.path.join(DOCS_DIR, name), "r", encoding="utf-8") as f:
            text = f.read()
        for i, chunk in enumerate(chunk_text(text)):
            ids.append(f"{name}-{i}")
            texts.append(chunk)
            metas.append({"source": name, "chunk": i})
    embeddings = model.encode(texts).tolist()
    col.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metas)
    print(f"Stored {len(texts)} chunks from {len(set(m['source'] for m in metas))} file(s).")


def search(question, k=3):
    col = client.get_collection("notes")
    q = model.encode([question]).tolist()
    res = col.query(query_embeddings=q, n_results=k)
    hits = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({"text": doc, "source": meta["source"], "score": 1 - dist})
    return hits


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "ingest":
        ingest()
    elif len(sys.argv) >= 3 and sys.argv[1] == "search":
        for h in search(" ".join(sys.argv[2:])):
            print(f"[{h['source']}] score={h['score']:.2f}")
            print(h["text"])
            print("-" * 40)
    else:
        print('Usage:  python rag.py ingest   |   python rag.py search "your question"')