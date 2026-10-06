# api/index.py
import os
import math
from typing import List, Dict, Any
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

# Enable CORS for any origin (needed for browser dashboards)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def percentile(values: List[float], p: float) -> float:
    """Compute the p-th percentile (0–100) using nearest-rank method."""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    # nearest-rank: rank = ceil(p/100 * n), clamp to [1, n]
    rank = math.ceil((p / 100.0) * n)
    rank = max(1, min(rank, n))
    return sorted_vals[rank - 1]

@app.post("/")
async def analytics_endpoint(payload: Dict[str, Any]):
    """
    Expected JSON body:
    {
      "regions": ["apac", "amer", ...],
      "threshold_ms": 180
    }

    We assume there's a global telemetry bundle (e.g., q-vercel-latency.json)
    loaded as a list of records with fields:
      - region: str
      - latency_ms: float
      - uptime: float (0–1 or 0–100; we'll treat as 0–1)
    For this assignment, we'll hard-code a small sample bundle.
    In a real system you'd fetch from storage or an env var.
    """

    regions: List[str] = payload.get("regions", [])
    threshold_ms: float = payload.get("threshold_ms", 180.0)

    # Sample telemetry bundle (replace with real data or load from env/file if allowed)
    # This mimics what q-vercel-latency.json might contain.
    telemetry = [
        {"region": "apac", "latency_ms": 120.0, "uptime": 0.99},
        {"region": "apac", "latency_ms": 210.0, "uptime": 0.97},
        {"region": "apac", "latency_ms": 150.0, "uptime": 0.98},
        {"region": "amer", "latency_ms": 90.0, "uptime": 0.999},
        {"region": "amer", "latency_ms": 180.0, "uptime": 0.995},
        {"region": "amer", "latency_ms": 200.0, "uptime": 0.990},
        {"region": "eu", "latency_ms": 130.0, "uptime": 0.98},
        {"region": "eu", "latency_ms": 140.0, "uptime": 0.97},
    ]

    result: Dict[str, Dict[str, Any]] = {}

    for region in regions:
        # Filter records for this region
        recs = [r for r in telemetry if r.get("region") == region]
        if not recs:
            # No data for this region
            result[region] = {
                "avg_latency": 0.0,
                "p95_latency": 0.0,
                "avg_uptime": 0.0,
                "breaches": 0,
            }
            continue

        latencies = [r["latency_ms"] for r in recs]
        uptimes = [r["uptime"] for r in recs]

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = percentile(latencies, 95)
        avg_uptime = sum(uptimes) / len(uptimes)
        breaches = sum(1 for r in recs if r["latency_ms"] > threshold_ms)

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches,
        }

    return JSONResponse(content=result)