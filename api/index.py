# api/index.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, List

app = FastAPI()

# Enable CORS for any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from Vercel"}

@app.post("/")
async def analytics_endpoint(payload: Dict[str, Any]):
    """
    Expected JSON body:
    {
      "regions": ["apac", "amer", ...],
      "threshold_ms": 180
    }

    For now, return a simple response with CORS headers explicitly set.
    """

    regions: List[str] = payload.get("regions", [])
    threshold_ms: float = payload.get("threshold_ms", 180.0)

    # Temporary dummy metrics (replace with real computation later)
    result = {}
    for region in regions:
        result[region] = {
            "avg_latency": 0.0,
            "p95_latency": 0.0,
            "avg_uptime": 0.0,
            "breaches": 0,
        }

    # Explicitly add CORS headers to the response
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    return JSONResponse(content=result, headers=headers)