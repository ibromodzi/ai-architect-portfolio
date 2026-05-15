# Agentic AI Architect Sprint

A 14-day self-directed sprint building production-grade agentic AI systems
with Google Agent Development Kit (ADK) and Gemini.

Based on *Building Agentic AI Systems* — Biswas & Talukdar (Packt).

## Portfolio Projects

| Project | Domain | Status |
|---|---|---|
| FinSight Agent | Finance — portfolio analysis & risk reports | 🔨 In progress |
| ClinAssist Agent | Health — RAG-powered symptom triage | ⏳ Week 2 |
| DevOps AutoPilot | Tech — autonomous CI/CD monitoring | ⏳ Week 2 |

## Daily Progress

| Day | Topic | Folder |
|---|---|---|
| 1 | ADK Orientation & Agent Fundamentals | `day-1/` |
| 2 | Tool Use & Function Calling | `day-2/` |
| 3 | Memory & State Management | `day-3/` |
| 4–6 | Multi-Agent Orchestration + FinSight | `day-4/` – `day-6/` |
| 7 | Architecture Review & FinSight Publication | `day-7/` |
| 8–10 | Human-in-the-Loop + ClinAssist | `day-8/` – `day-10/` |
| 11–13 | Autonomous Agents + DevOps AutoPilot | `day-11/` – `day-13/` |
| 14 | Portfolio Day | `day-14/` |

## Stack

- **Runtime:** Python 3.11+ / venv
- **Framework:** [Google ADK](https://adk.dev) (`pip install google-adk`)
- **LLM:** Gemini 2.5 Flash via Google AI Studio
- **IDE:** VS Code

## Setup

```bash
git clone https://github.com/ibromodzi/ai-architect-portfolio.git
cd ai-architect-portfolio
python -m venv .venv && source .venv/bin/activate
pip install google-adk
```

Copy `.env.example` to `.env` inside the relevant day folder and add your
[Google AI Studio API key](https://aistudio.google.com/apikey).

## Notes

Never commit `.env` files. The `.gitignore` at the root covers all day folders.
