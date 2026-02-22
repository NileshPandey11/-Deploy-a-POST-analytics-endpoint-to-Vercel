from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

# CORS allow karna taaki dashboard se call ho sake
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Data load karna
with open('q-vercel-latency.json', 'r') as f:
    telemetry_data = json.load(f)

@app.post("/api/metrics")
async def get_metrics(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)
    
    results = {}
    
    for r in regions:
        # Region ke hisaab se data filter karna
        subset = [d for d in telemetry_data if d['region'] == r]
        if not subset:
            continue
            
        latencies = sorted([d['latency_ms'] for d in subset])
        uptimes = [d['uptime_pct'] for d in subset]
        
        # Calculations
        avg_lat = sum(latencies) / len(latencies)
        # P95 Calculation
        p95_idx = int(len(latencies) * 0.95)
        p95_lat = latencies[min(p95_idx, len(latencies) - 1)]
        avg_upt = sum(uptimes) / len(uptimes)
        breaches = len([l for l in latencies if l > threshold])
        
        results[r] = {
            "avg_latency": round(avg_lat, 2),
            "p95_latency": round(p95_lat, 2),
            "avg_uptime": round(avg_upt, 3),
            "breaches": breaches
        }
        
    return results