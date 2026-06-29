import os
import sys
import json
import asyncio
import time
import argparse

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(base_dir, "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from generate_demo import main as generate_demo_main

async def run_benchmark(iterations: int):
    print(f"--- Starting Benchmark Runner ({iterations} iterations) ---")

    latencies = []
    failures = 0
    replay_ids = set()

    for i in range(iterations):
        start_time = time.time()
        try:
            await generate_demo_main()
            latency = time.time() - start_time
            latencies.append(latency)

            # Grab replay id
            manifest_path = os.path.join(base_dir, "artifacts", "current", "manifest.json")
            if os.path.exists(manifest_path):
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                    if "replay_identifier" in manifest:
                        replay_ids.add(manifest["replay_identifier"])

        except Exception as e:
            print(f"Iteration {i+1} failed: {e}")
            failures += 1

    # Calculate stats
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    latencies.sort()
    median_latency = latencies[len(latencies)//2] if latencies else 0.0
    p95_latency = latencies[int(len(latencies)*0.95)] if latencies else 0.0
    std_dev = (sum((lat - avg_latency) ** 2 for lat in latencies) / len(latencies)) ** 0.5 if latencies else 0.0
    determinism_rate = (1.0 / len(replay_ids)) if replay_ids else 0.0
    failure_rate = failures / iterations

    report = {
        "iterations": iterations,
        "average_latency": avg_latency,
        "median_latency": median_latency,
        "p95_latency": p95_latency,
        "standard_deviation": std_dev,
        "determinism_rate": determinism_rate,
        "failure_rate": failure_rate,
        "cache_hit_ratio": 0.0,  # Stubbed out unless we mock cache stats
        "cache_miss_ratio": 0.0,
        "memory_usage": 0.0      # Stubbed out unless using psutil
    }

    out_path = os.path.join(base_dir, "benchmark_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Benchmark complete. Report saved to {out_path}")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run benchmarks")
    parser.add_argument("--iterations", type=int, default=10, help="Number of iterations")
    args = parser.parse_args()

    asyncio.run(run_benchmark(args.iterations))
