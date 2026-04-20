# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95 > 1000ms`
- Impact: tail latency breaches SLO
- First checks:
  1. Open top slow traces in the last 1h
  2. Compare RAG span vs LLM span
  3. Check if incident toggle `rag_slow` is enabled
- Mitigation:
  - truncate long queries
  - fallback retrieval source
  - lower prompt size

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 1%`
- Impact: users receive failed responses
- First checks:
  1. Group logs by `error_type`
  2. Inspect failed traces
  3. Determine whether failures are LLM, tool, or schema related
- Mitigation:
  - rollback latest change
  - disable failing tool
  - retry with fallback model

## 3. Budget threshold exceeded
- Severity: P2
- Trigger: `total_cost_usd > $2.0`
- Impact: burn rate exceeds budget
- First checks:
  1. Split traces by feature and model
  2. Compare tokens_in/tokens_out
  3. Check if `cost_spike` incident was enabled
- Mitigation:
  - shorten prompts
  - route easy requests to cheaper model
  - apply prompt cache

## 4. Quality degradation
- Severity: P3
- Trigger: `quality_avg < 0.85`
- Impact: agent responses are becoming less accurate
- First checks:
  1. Review recent feedback in Langfuse
  2. Check if a new prompt version was deployed
  3. Verify if retrieval (RAG) is returning irrelevant docs
- Mitigation:
  - adjust temperature
  - roll back prompt version
  - improve search weights
