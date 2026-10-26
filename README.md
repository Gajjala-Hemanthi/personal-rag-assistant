PERSONAL RAG ASSISTANT



A voice-enabled assistant that answers questions from my own notes, cites its sources, and says "I don't know" when the notes cannot answer.



!\[Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python\&logoColor=white)

!\[FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi\&logoColor=white)

!\[ChromaDB](https://img.shields.io/badge/ChromaDB-vector%20store-FF6F00)

!\[Gemini](https://img.shields.io/badge/Gemini-LLM-4285F4?logo=google\&logoColor=white)

!\[Kotlin](https://img.shields.io/badge/Kotlin-Android-7F52FF?logo=kotlin\&logoColor=white)

!\[Cost](https://img.shields.io/badge/Cost-%E2%82%B90-brightgreen)



Android app (Kotlin, Jetpack Compose) → FastAPI backend → RAG with reranking → Gemini



\## Contents



\- \[Highlights](#highlights)

\- \[Architecture](#architecture)

\- \[Request flow](#request-flow)

\- \[How the RAG pipeline works](#how-the-rag-pipeline-works)

\- \[Evaluation](#evaluation)

\- \[What I learned](#what-i-learned)

\- \[Demo](#demo)

\- \[Tech stack](#tech-stack)

\- \[Project structure](#project-structure)

\- \[Run it yourself](#run-it-yourself)

\- \[Limitations](#limitations)

\- \[Roadmap](#roadmap)



\## Highlights



| Feature | Why it matters |

|---|---|

| Retrieval-Augmented Generation | Answers come from my own notes, not the model's memory |

| Source citations | Every answer names the file it came from |

| Refuses when unsure | Says "I don't know based on my notes" instead of guessing |

| Cross-encoder reranking | Separates answerable from unanswerable questions |

| Evaluation-driven | Every change was measured and logged in `results.txt` |

| Voice in, voice out | Speech recognition and text-to-speech on Android |

| Voice commands | "Open WhatsApp", "open camera" and more |

| No keys in the app | The API key lives only on the backend |

| Free to build | Gemini free tier, local embeddings, local vector DB |



\## Architecture



```mermaid

flowchart LR

&#x20;   subgraph PHONE\["Android App (Kotlin + Compose)"]

&#x20;       A1\["Voice or text input"]

&#x20;       A2\["Spoken and written answer"]

&#x20;   end



&#x20;   subgraph BACKEND\["FastAPI Backend (Python)"]

&#x20;       B1\["POST /ask"]

&#x20;       B2\["Embed question (MiniLM)"]

&#x20;       B3\[("ChromaDB")]

&#x20;       B4\["Cross-encoder reranker"]

&#x20;       B5{"Best score >= -4 ?"}

&#x20;       B6\["I don't know"]

&#x20;       B7\["Gemini: answer from notes only"]

&#x20;   end



&#x20;   A1 -->|"HTTP JSON"| B1

&#x20;   B1 --> B2

&#x20;   B2 --> B3

&#x20;   B3 -->|"top 5 chunks"| B4

&#x20;   B4 --> B5

&#x20;   B5 -->|"No"| B6

&#x20;   B5 -->|"Yes, keep top 3"| B7

&#x20;   B6 --> A2

&#x20;   B7 -->|"answer, sources, latency"| A2

```



\## Request flow



```mermaid

sequenceDiagram

&#x20;   autonumber

&#x20;   actor You

&#x20;   participant App as Android App

&#x20;   participant API as FastAPI

&#x20;   participant DB as ChromaDB

&#x20;   participant RR as Reranker

&#x20;   participant LLM as Gemini



&#x20;   You->>App: "What phone did I test on?"

&#x20;   App->>API: POST /ask

&#x20;   API->>DB: embed question, fetch top 5 chunks

&#x20;   DB-->>API: 5 candidate chunks

&#x20;   API->>RR: score (question, chunk) pairs

&#x20;   RR-->>API: relevance scores

&#x20;   alt best score below -4

&#x20;       API-->>App: "I don't know based on my notes."

&#x20;   else relevant notes found

&#x20;       API->>LLM: question + top 3 chunks + strict rules

&#x20;       LLM-->>API: grounded answer with source file

&#x20;       API-->>App: answer + sources + latency

&#x20;   end

&#x20;   App-->>You: shows and speaks the answer

```



\## How the RAG pipeline works



\### Ingest (offline)



```mermaid

flowchart LR

&#x20;   D\["docs/\*.txt"] --> S\["Split by sentence (\~200 characters)"]

&#x20;   S --> E\["Embed with all-MiniLM-L6-v2"]

&#x20;   E --> V\[("ChromaDB, cosine similarity")]

```



\### Answer (online)



| Step | What happens | Tool |

|---|---|---|

| Retrieve | Find the 5 chunks closest to the question | MiniLM + ChromaDB |

| Rerank | Read question and chunk together, then rescore | ms-marco-MiniLM-L-6-v2 |

| Gate | Best score below -4 means refuse | Threshold chosen from data |

| Generate | Answer using only the top 3 chunks and cite the source | Gemini |



\## Evaluation



Every change was measured on a test set and logged in \[results.txt](results.txt).



```mermaid

flowchart LR

&#x20;   V1\["v1 Baseline<br/>refusals 25%"] --> V2\["v2 Threshold 0.22<br/>refusals 75%<br/>hit@3 dropped to 88%"]

&#x20;   V2 --> V3\["v3 Gate on top chunk only"]

&#x20;   V3 --> V4\["v4 Fetch 5 + rerank<br/>hit@3 back to 100%"]

&#x20;   V4 --> V5\["v5 Reranker score as gate<br/>refusals 100%"]

```



| Version | Change | hit@1 | hit@3 | Correct refusals |

|---|---|:---:|:---:|:---:|

| v1 | Baseline: 200-char chunks, embedding threshold 0.15 | 88% | 100% | 25% |

| v2 | Per-chunk threshold 0.22 | 88% | 88% | 75% |

| v3 | Threshold on the top chunk only (7 chunks) | 88% | 88% | 75% |

| v4 | Fetch 5, rerank, keep 3 | 88% | 100% | 75% |

| v5 | Reranker score as the refusal gate (-4) | 88% | 100% | \*\*100%\*\* |



Held-out set (6 new questions, not used for tuning): hit@1 67%, hit@3 100%, refusals 100%.



Metrics:



\- \*\*hit@1\*\*: the correct chunk was ranked first

\- \*\*hit@3\*\*: the correct chunk was among the top 3

\- \*\*Correct refusals\*\*: unanswerable questions that were properly rejected



\## What I learned



\*\*1. Fixed-size chunking cut words in half.\*\*

Splitting every 300 characters produced chunks like `cs, LLM APIs and RAG.` Splitting by sentence fixed it and raised the top score from 0.40 to 0.52.



\*\*2. A tiny index hides retrieval problems.\*\*

With 3 chunks, "top 3" returned everything, so retrieval looked perfect. After adding a second notes file, "what projects have I built?" failed: the goal chunk won on shared words while the chunks that actually listed projects ranked lower.



\*\*3. Embedding similarity could not tell answerable from unanswerable.\*\*

"What is my salary?" scored 0.27, higher than the answerable "What is my goal?" at 0.26, so no threshold could separate them. The cross-encoder scored answerable questions at 0.26 or higher and unanswerable ones at -9.4 or lower, a gap of about 10 points.



\*\*4. A fix caused a regression.\*\*

Raising the threshold (v2) improved refusals but broke broad questions that need several weaker chunks. Applying the threshold to the top chunk only (v3) fixed it. Measuring every change caught this.



\*\*5. Keep keys off the device.\*\*

An early version of the app held the API key. The final app calls the backend and holds no key.



\## Demo



| Answer with a source | Refusal |

|:---:|:---:|

| !\[answer](screenshots/answer.png) | !\[refusal](screenshots/refusal.png) |

| "What phone did I test on?" | "What is my salary?" |



Demo video: \_add link here\_



\## Tech stack



| Layer | Technology |

|---|---|

| Mobile | Kotlin, Jetpack Compose, SpeechRecognizer, TextToSpeech |

| Backend | Python, FastAPI, Uvicorn |

| Embeddings | sentence-transformers all-MiniLM-L6-v2 |

| Vector DB | ChromaDB (cosine similarity) |

| Reranker | cross-encoder ms-marco-MiniLM-L-6-v2 |

| LLM | Google Gemini (free tier) |



\## Project structure



```

rag\_project/

├── rag.py              # ingest + vector search

├── ask.py              # rerank, refusal gate, Gemini answer

├── api.py              # FastAPI: /ask  /ingest  /health

├── eval.py             # tuning test set + metrics

├── eval2.py            # tuning set + held-out set

├── sweep.py, ksweep.py, rerank\_test.py, rscore.py   # experiments

├── results.txt         # experiment log

├── docs/               # source notes (the knowledge base)

├── requirements.txt

└── .gitignore

```



\## Run it yourself



```bash

\# 1. Install

pip install -r requirements.txt



\# 2. Set your Gemini key (never commit it)

set GEMINI\_API\_KEY=your\_key\_here          # Windows

\# export GEMINI\_API\_KEY=your\_key\_here     # Mac / Linux



\# 3. Build the index from docs/

python rag.py ingest



\# 4. Ask a question

python ask.py "what phone did I test on?"



\# 5. Run the evaluation

python eval2.py



\# 6. Start the API

python -m uvicorn api:app --port 8000

```



Interactive API docs: `http://127.0.0.1:8000/docs`



| Method | Path | Purpose |

|---|---|---|

| GET | `/health` | Check the server is up |

| POST | `/ask` | `{"question": "..."}` returns answer, sources, latency |

| POST | `/ingest` | Rebuild the index from `docs/` |



\## Limitations



\- Small test sets (12 tuning, 6 held-out): results show direction, not a guarantee

\- The index is tiny (7 chunks), and hit@1 is the weak spot on broad questions

\- The refusal threshold was chosen from the same data used to test it, which is why the held-out set matters

\- The Android app currently reaches the backend over a USB link (`adb reverse`), not a public URL



\## Roadmap



\- \[x] RAG pipeline with citations

\- \[x] Refusal when notes cannot answer

\- \[x] Evaluation with before and after numbers

\- \[x] Cross-encoder reranking

\- \[x] FastAPI backend

\- \[x] Android app with voice

\- \[ ] Hybrid search (keyword + embeddings) to lift hit@1

\- \[ ] Tool calling (live prices, weather)

\- \[ ] Larger evaluation set with automatic answer grading

\- \[ ] Public deployment of the backend



Built by Gajjala Hemanthi

