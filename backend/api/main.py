from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from . import search, tasks

app = FastAPI(title="OpenWords API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/search")
def search_text(q: str = Query(..., min_length=2), top_k: int = 20):
    return search.hybrid_search(q, k=top_k)

@app.post("/ingest/url")
def ingest_url(url: str):
    job_id = tasks.ingest_from_url.delay(url).id
    return {"job_id": job_id}
    return {"job_id": job_id}
