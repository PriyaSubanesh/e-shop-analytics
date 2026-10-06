# api/index.py
import math
from typing import Dict, Any, List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    rank = math.ceil((p / 100.0) * n)
    rank = max(1, min(rank, n))
    return sorted_vals[rank - 1]

# Sample telemetry bundle (replace with real data later if needed)
TELEMETRY = [
    {"region": "apac", "latency_ms": 120.0, "uptime": 0.99},
    {"region": "apac", "latency_ms": 210.0, "uptime": 0.97},
    {"region": "apac", "latency_ms": 150.0, "uptime": 0.98},
    {"region": "amer", "latency_ms": 90.0, "uptime": 0.999},
    {"region": "amer", "latency_ms": 180.0, "uptime": 0.995},
    {"region": "amer", "latency_ms": 200.0, "uptime": 0.990},
    {"region": "eu", "latency_ms": 130.0, "uptime": 0.98},
    {"region": "eu", "latency_ms": 140.0, "uptime": 0.97},
]

@app.get("/")
def read_root():
    return {"message": "Hello from Vercel"}

@app.post("/")
async def analytics_endpoint(payload: Dict[str, Any]):
    regions: List[str] = payload.get("regions", [])
    threshold_ms: float = payload.get("threshold_ms", 180.0)

    result: Dict[str, Dict[str, Any]] = {}

    for region in regions:
        recs = [r for r in TELEMETRY if r.get("region") == region]
        if not recs:
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

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    return JSONResponse(content=result, headers=headers)