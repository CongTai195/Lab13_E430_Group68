import yaml
import requests
import sys
import os

# Configuration
METRICS_URL = "http://127.0.0.1:8000/metrics"
ALERTS_CONFIG = "config/alert_rules.yaml"

def load_alert_rules():
    if not os.path.exists(ALERTS_CONFIG):
        print(f"Error: {ALERTS_CONFIG} not found")
        sys.exit(1)
    with open(ALERTS_CONFIG, "r") as f:
        return yaml.safe_load(f).get("alerts", [])

def fetch_metrics():
    try:
        response = requests.get(METRICS_URL)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching metrics: {e}")
        sys.exit(1)

def evaluate_condition(condition, metrics):
    # Simplified parser for conditions like 'latency_p95 > 3000'
    # Condition format: <metric_name> <operator> <value>
    parts = condition.split()
    if len(parts) < 3:
        return False
    
    metric_name = parts[0]
    operator = parts[1]
    threshold = float(parts[2])
    
    current_value = metrics.get(metric_name)
    if current_value is None:
        return False
    
    if operator == ">":
        return current_value > threshold
    elif operator == "<":
        return current_value < threshold
    elif operator == "==":
        return current_value == threshold
    
    return False

def main():
    print("--- Alert Verification System ---")
    rules = load_alert_rules()
    metrics = fetch_metrics()
    
    firing_count = 0
    for rule in rules:
        name = rule.get("name")
        condition = rule.get("condition")
        severity = rule.get("severity")
        
        is_firing = evaluate_condition(condition, metrics)
        status = "[FIRING]" if is_firing else "[RESOLVED]"
        if is_firing:
            firing_count += 1
        
        print(f"{status} {name} ({severity})")
        print(f"  Condition: {condition}")
        print(f"  Current:   {metrics.get(condition.split()[0])}")
        print(f"  Runbook:   {rule.get('runbook')}")
        print("-" * 30)

    if firing_count == 0:
        print("\nAll systems normal. No alerts firing.")
    else:
        print(f"\nCRITICAL: {firing_count} alerts are currently firing!")

if __name__ == "__main__":
    main()
