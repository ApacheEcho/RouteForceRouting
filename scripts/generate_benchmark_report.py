#!/usr/bin/env python3
"""
Generate performance benchmark report for GitHub Actions.
"""
import json
import sys
import os


def main():
    print("## 🎯 Performance Benchmark Results")

    if not os.path.exists("benchmark_results.json"):
        print("⚠️ No benchmark results file found (benchmark_results.json)")
        print("This may indicate that benchmarks failed to run or complete.")
        return

    try:
        with open("benchmark_results.json", "r") as f:
            data = json.load(f)

        benchmarks = data.get("benchmarks", [])
        if not benchmarks:
            print("⚠️ No benchmark data found in results")
            return

        print("")
        print("## 📊 Benchmark Summary")
        print(
            "| Test | Mean Time (s) | Min Time (s) | Max Time (s) | Status |"
        )
        print(
            "|------|---------------|--------------|--------------|--------|"
        )

        for benchmark in benchmarks:
            name = (
                benchmark.get("name", "Unknown")
                .replace("test_", "")
                .replace("_performance", "")
            )
            stats = benchmark.get("stats", {})
            mean = stats.get("mean", 0)
            min_time = stats.get("min", 0)
            max_time = stats.get("max", 0)

            # Determine status based on performance
            if mean < 1.0:
                status = "🟢 Excellent"
            elif mean < 3.0:
                status = "🟡 Good"
            elif mean < 10.0:
                status = "🟠 Acceptable"
            else:
                status = "🔴 Needs Optimization"

            print(
                f"| {name} | {mean:.4f} | {min_time:.4f} | {max_time:.4f} | {status} |"
            )

        print("")
        print(f"📈 Total benchmarks: {len(benchmarks)}")

        # Calculate overall performance
        avg_time = sum(
            b.get("stats", {}).get("mean", 0) for b in benchmarks
        ) / len(benchmarks)
        if avg_time < 2.0:
            print("✅ Overall Performance: Excellent")
        elif avg_time < 5.0:
            print("🟡 Overall Performance: Good")
        else:
            print("⚠️ Overall Performance: Needs Improvement")

    except Exception as e:
        print(f"❌ Error parsing benchmark results: {e}")
        print("📋 Raw benchmark file contents:")
        try:
            with open("benchmark_results.json", "r") as f:
                print(f.read()[:500])  # First 500 chars
        except:
            print("Could not read benchmark file")


if __name__ == "__main__":
    main()
