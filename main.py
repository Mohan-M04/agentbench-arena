import os
import sys
import argparse

# Change working directory to backend so all relative imports & .env work
backend_dir = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AgentBench Arena: Web Observatory & CLI Benchmark Runner")
    parser.add_argument("--suite", type=str, default=None, help="Run specific benchmark suite in CLI mode (e.g. chaos_suite, quick_check)")
    parser.add_argument("--runs", type=int, default=10, help="Repeated runs per task")
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed for reproducibility")
    parser.add_argument("--export", type=str, default="all", choices=["all", "json", "csv", "markdown", "none"], help="Export formats")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Web server host")
    parser.add_argument("--port", type=int, default=8000, help="Web server port")

    args, unknown = parser.parse_known_args()

    if args.suite:
        # One-Click CLI Reproduction Mode
        print("=" * 65)
        print("🛡️  AGENTBENCH ARENA — DETERMINISTIC BENCHMARK RUNNER")
        print("=" * 65)
        print(f"Suite: {args.suite} | Seed: {args.seed} | Runs: {args.runs} | Export: {args.export}")
        import random
        random.seed(args.seed)
        
        repo_root = os.path.dirname(os.path.abspath(__file__))
        scripts_dir = os.path.join(repo_root, "scripts")
        sys.path.insert(0, scripts_dir)
        from generate_trace_evidence import generate_evidence
        generate_evidence(runs_count=args.runs, export=args.export)

        # Create specific seed folder: results/chaos_suite_seed_{args.seed}/
        import shutil
        seed_dir = os.path.join(repo_root, "results", f"chaos_suite_seed_{args.seed}")
        os.makedirs(seed_dir, exist_ok=True)
        for agent_name in ["react_retry_fallback", "langgraph", "custom_json", "naive_react"]:
            src = os.path.join(repo_root, "results", agent_name, "summary.json")
            if os.path.exists(src):
                shutil.copy(src, os.path.join(seed_dir, f"{agent_name}_summary.json"))

        print("\n" + "=" * 65)
        print("✅ REPRODUCTION COMPLETE: Exact benchmark evidence written to:")
        print(f"  • {seed_dir}")
        print(f"  • {os.path.join(repo_root, 'results', 'benchmark_summary.csv')}")
        print(f"  • {os.path.join(repo_root, 'results', 'task_level_matrix.csv')}")
        print(f"  • {os.path.join(repo_root, 'reports')}")
        print("=" * 65)
        sys.exit(0)

    # Web Observatory Server Mode (Default)
    os.chdir(backend_dir)
    import uvicorn
    uvicorn.run("main:app", host=args.host, port=args.port, reload=True)
