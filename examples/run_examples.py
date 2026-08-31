import os
import sys
import glob
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app

def run_all_benchmarks():
    client = TestClient(app)
    example_files = sorted(glob.glob(os.path.join(os.path.dirname(__file__), "*.json")))
    
    print("=" * 80)
    print("AI TEACHER VISUAL EXPLANATION ENGINE - BENCHMARK RUNNER")
    print("=" * 80)
    print(f"Discovered {len(example_files)} benchmark example payloads.\n")

    results = []
    start_all = time.time()

    for idx, fpath in enumerate(example_files, 1):
        with open(fpath, "r", encoding="utf-8") as f:
            payload = json.load(f)

        print(f"[{idx}/{len(example_files)}] Testing: '{payload.get('concept')}' (Topic: {payload.get('topic')})")
        t0 = time.time()
        response = client.post("/generate-visual", json=payload)
        elapsed = (time.time() - t0) * 1000

        if response.status_code == 200:
            data = response.json()
            primary_type = data.get("visual_type")
            sec_count = len(data.get("secondary_visuals", []))
            conf = data.get("selector_metadata", {}).get("confidence", 0)
            url = data.get("visual_url")

            print(f"    ? Selected:   {primary_type.upper()} (Confidence: {conf:.2f})")
            print(f"    ? Title:      {data.get('title')}")
            print(f"    ? Visual URL: {url}")
            print(f"    ? Secondary:  ({sec_count}) {[s.get('visual_type') for s in data.get('secondary_visuals', [])]}")
            print(f"    ? Latency:    {elapsed:.1f}ms\n")

            results.append({
                "concept": payload.get("concept"),
                "status": "PASS",
                "type": primary_type,
                "confidence": conf,
                "secondary_count": sec_count,
                "latency_ms": elapsed
            })
        else:
            print(f"    ? FAILED with status {response.status_code}: {response.text}\n")
            results.append({
                "concept": payload.get("concept"),
                "status": "FAIL",
                "error": response.text
            })

    total_time = time.time() - start_all
    print("=" * 80)
    print("BENCHMARK SUMMARY")
    print("=" * 80)
    passed = sum(1 for r in results if r["status"] == "PASS")
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {len(results) - passed} | Total Time: {total_time:.2f}s")
    print("=" * 80)

if __name__ == "__main__":
    run_all_benchmarks()
