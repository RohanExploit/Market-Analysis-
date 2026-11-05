# Market Research Agent

An AI-based market research agent that accepts a research topic (product, company, or industry), gathers up-to-date web information, and returns a structured summary.

## Problem Solved
Manual market research is slow and scattered across many sources. This project provides a faster, structured flow for early-stage decision-making by:
- understanding a research query,
- collecting web information through Jina Search + Reader,
- synthesizing results with Gemini (when configured), and
- producing a structured report.

## Agent Type
This implementation follows a **Goal-Based Intelligent Agent** design with:
- **Tool-using behavior:** Jina Search/Reader API calls for web data gathering,
- **Model-based memory:** previous user topics are preserved for follow-up context,
- **Adaptive behavior:** multiple planned queries are executed until enough sources are collected.

## PEAS Summary
- **Performance Measure:** relevance, structure, source freshness, and time saved.
- **Environment:** user query, web pages, internet, and deployment platforms (for example Dify).
- **Actuators:** structured report output in JSON/chat format.
- **Sensors:** topic input, web search results, reader content, and conversation history.

## Working Flow
1. Receive research topic.
2. Plan market-research sub-queries.
3. Use Jina Search and Jina Reader to gather source content.
4. Analyze/summarize with Gemini (or fallback summary when Gemini is unavailable).
5. Return a structured report with:
   - market overview
   - key trends
   - major competitors
   - customer needs
   - challenges
   - growth opportunities
   - source list

## Setup
Python 3.10+ recommended.

Optional environment variables:
- `JINA_API_KEY`
- `GEMINI_API_KEY`

## Usage
```bash
python src/market_research_agent.py "Market analysis of electric vehicles in India"
```

## Tests
```bash
python -m unittest discover -s tests -v
```

## Deployment Note
The activity report deployment link is:
- https://udify.app/agent/NLlChwPOK1h2OmxR

API keys should be configured securely in the deployment platform and not exposed in UI.
