from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


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
async def health():
    return {"ok": True}

@app.get("/search")
async def search_text(q: str = Query(..., min_length=2), top_k: int = 20):
    if not 1 <= top_k <= 50:
        return JSONResponse(
            status_code=400,
            content={
                "error": "invalid_top_k",
                "message": "top_k must be between 1 and 50",
            },
        )
    try:
        return search.hybrid_search(q, k=top_k)
    except Exception as e:  # pragma: no cover - future real search may raise
        return JSONResponse(
            status_code=500,
            content={"error": "search_failed", "message": str(e)},
        )

@app.post("/ingest/url")
async def ingest_url(url: str):
    try:
        job_id = tasks.ingest_from_url.delay(url).id
        return {"job_id": job_id}
    except Exception as e:  # pragma: no cover - future real ingest may raise
        return JSONResponse(
            status_code=500,
            content={"error": "ingest_failed", "message": str(e)},
        )
