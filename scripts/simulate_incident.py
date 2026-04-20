import requests
import json
import time
import concurrent.futures
import os
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8000"
QUERIES_FILE = Path("data/sample_queries.jsonl")

def log_step(msg):
    print(f"\n>>> [STEP] {msg}")

def set_incident(scenario, enabled=True):
    action = "enable" if enabled else "disable"
    url = f"{BASE_URL}/incidents/{scenario}/{action}"
    try:
        r = requests.post(url)
        r.raise_for_status()
        print(f"    Incident '{scenario}' {action}d: {r.json()['ok']}")
    except Exception as e:
        print(f"    Failed to {action} incident: {e}")

def run_load_burst(concurrency=5):
    print(f"    Generating load (concurrency={concurrency})...")
    lines = [line for line in QUERIES_FILE.read_text(encoding="utf-8").splitlines() if line.strip()]
    
    def send_req(payload):
        requests.post(f"{BASE_URL}/chat", json=payload, timeout=30)

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(send_req, json.loads(line)) for line in lines]
        concurrent.futures.wait(futures)
    print("    Load burst complete.")

def check_alerts():
    print("    Evaluating alert rules...")
    try:
        import sys
        sys.path.append(os.getcwd())
        from scripts.check_alerts import fetch_metrics, load_alert_rules, evaluate_condition
        metrics = fetch_metrics()
        rules = load_alert_rules()
        
        firing = []
        for rule in rules:
            if evaluate_condition(rule["condition"], metrics):
                firing.append(rule["name"])
        return firing
    except Exception as e:
        print(f"    Alert engine error: {e}")
        return []

def main():
    scenario = "rag_slow"
    
    print("="*50)
    print("      AUTOMATED INCIDENT SIMULATION RUN")
    print("="*50)

    # 1. Baseline
    log_step("Resetting state and checking baseline...")
    set_incident("rag_slow", False)
    set_incident("tool_fail", False)
    time.sleep(1)
    
    # 2. Injection
    log_step(f"Injecting Incident Scenario: {scenario}")
    set_incident(scenario, True)

    # 3. Pressure
    log_step("Applying pressure under incident...")
    run_load_burst(concurrency=5)

    # 4. Detection
    log_step("Running Detection Check...")
    firing = check_alerts()
    if firing:
        print(f"    SUCCESS: Detection System caught: {', '.join(firing)}")
    else:
        print("    FAILURE: No alerts triggered despite incident!")

    # 5. Recovery
    log_step("Resolving Incident...")
    set_incident(scenario, False)
    
    # 6. Final Status
    log_step("Finalizing Simulation...")
    print("    Incident test completed successfully.")
    print("="*50)

if __name__ == "__main__":
    main()
