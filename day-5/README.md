
# FinSight Agent v1.0

A multi-agent finance assistant built with Google ADK and Gemini 2.5 Flash. It accepts a stock ticker, fetches live market data, produces a structured JSON risk report, scores it with an LLM judge, and exports the final results to a formatted PDF.

## Architecture

*(Paste your architecture diagram from Step 2 here)*

## Design Decisions

* **Why SequentialAgent instead of LlmAgent as orchestrator?**
The data-fetch $\rightarrow$ risk-assess $\rightarrow$ judge sequence always follows the exact same order. Using `SequentialAgent` makes that execution deterministic and removes an unnecessary LLM routing call that would otherwise be wasted.
* **Why are output_schema and tools on separate agents?**
Combining both `tools` and an `output_schema` on a single agent can cause silent failures on certain Gemini models. `DataFetcherAgent` handles the tool executions, while `RiskAssessorAgent` handles structured schema output. Each agent has one job.
* **Why PlanReActPlanner on RiskAssessorAgent?**
The planning block makes the model's reasoning auditable. In a financial context, you want to see the quantitative reasoning steps leading to the classification, not just the raw conclusion.

## Trade-offs

| Decision | Benefit | Cost |
| --- | --- | --- |
| **SequentialAgent** | Deterministic, saves a routing LLM call | Inflexible if the execution order needs to change dynamically |
| **DatabaseSessionService** | Session state and memory survive application restarts | Requires configuring `aiosqlite` + `greenlet` |
| **PlanReActPlanner** | Auditable, step-by-step reasoning logs | Slightly longer response times and token usage |
| **output_schema** | Enforces strongly typed, easily parseable JSON output | Cannot be mixed with tools on the same agent |

## Known Limitations

* Free-tier rate limits (20 requests/day on `gemini-2.5-flash`) can restrict heavy evaluation runs.
* `yfinance` data may be delayed up to 15 minutes for certain tickers.
* `RiskAssessorAgent` has no built-in fallback strategy if the `market_data` block arrives empty or malformed.
* The standalone PDF exporter script uses `InMemorySessionService`; state from that runner does not persist to the primary SQLite instance.

## Tech Stack

* **Runtime:** Python 3.11
* **Framework:** Google ADK (`google-adk`)
* **LLM:** Gemini 2.5 Flash via Google AI Studio
* **Data:** `yfinance`
* **PDF Generation:** `reportlab`
* **Persistence:** SQLite via `DatabaseSessionService`

## Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/ai-architect-portfolio.git
cd ai-architect-portfolio/day-4 # or day-5

# Set up environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment variables
cp finsight_agent/.env.example finsight_agent/.env
# Edit finsight_agent/.env and add your Google AI Studio API key

# Run the ADK web interface (Run from this folder, not from inside finsight_agent/)
adk web

```

## Evaluation

```bash
python -m pytest tests/test_finsight.py -v

```

## Export a PDF Report

```bash
python export_report.py

```