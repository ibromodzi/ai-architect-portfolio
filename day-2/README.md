# Day 2: Multi-Tool Agent

Agent: `multi_tool_agent` | Model: `gemini-2.5-flash` | Framework: Google ADK

## Tools

| Tool | Purpose |
|------|---------|
| `calculate` | Evaluates mathematical expressions |
| `convert_units` | Converts physical units (length, weight, temperature) |
| `format_timestamp` | Converts Unix timestamps to readable dates |

## Test Results

| Query | Tool Called | Result | Status |
|-------|-------------|--------|--------|
| `sqrt(256) + 15% of 200` | `calculate` | 46.0 | PASS |
| `Convert 100 km to miles` | `convert_units` | 62.1371 miles | PASS |
| `Unix timestamp 1748000000` | `format_timestamp` | Friday, 23 May 2025 at 11:33 UTC | PASS |
| `Convert 50 USD to NGN` | none | Refused — tool handles physical units only | PASS |
| `Calculate 10 / 0` | `calculate` | Returned error dict, did not crash | PASS |
| `Convert 100 parsecs to light-years` | `convert_units` | Returned unsupported conversion error | PASS |
| `Current time in Nigeria` | none | Refused — no real-time access | PASS |

## Observations

- Tool routing was correct on all queries. No hallucinated tool calls observed.
- The currency edge case (`50 USD to NGN`) was the highest-risk for misrouting to `calculate`. The explicit `Do NOT use for currency` in the docstring prevented this.
- All tools return `{"error": str}` on failure instead of raising exceptions, so the agent loop never crashed.
- The timestamp query prompted the agent to ask for a timezone offset before proceeding. Defaulting to UTC in the system prompt would remove this friction.