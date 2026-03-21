# biosamples-mcp

![Python 3.11](https://img.shields.io/badge/python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green) ![MCP](https://img.shields.io/badge/MCP-enabled-purple) ![Docker](https://img.shields.io/badge/docker-ready-blue) ![BioSamples API](https://img.shields.io/badge/BioSamples-EBI-orange)

A production-ready MCP (Model Context Protocol) server that makes the EMBL-EBI BioSamples database queryable by AI agents. Point an LLM at this server and it can search millions of biological samples, fetch rich metadata, and submit new samples — all through a clean tool interface.

## Inspiration

This project was inspired by the **EMBL-EBI Google Summer of Code 2026** project idea: *"MCP Server for BioSamples API"*. The goal is to bridge modern AI tooling with one of biology's most important public databases. Learn more at [EMBL-EBI GSoC 2026](https://www.ebi.ac.uk/about/events/gsoc/).

## Architecture

```
LLM Agent
    │
    ▼
MCP Server (FastAPI, port 8000)
    │   ├── search_biosamples
    │   ├── fetch_biosample
    │   └── submit_biosample
    │
    ▼
BioSamples REST API
(https://www.ebi.ac.uk/biosamples)
```

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Anas9-8/biosamples-mcp
cd biosamples-mcp

# Copy environment file and add your token (only needed for submit)
cp .env.example .env

# Start with Docker Compose
docker-compose up --build

# Check it's running
curl http://localhost:8000/health
# {"status": "ok", "version": "1.0.0"}

# List available tools
curl http://localhost:8000/tools
```

## MCP Tools

| Tool | Description | Required Input |
|------|-------------|----------------|
| `search_biosamples` | Search by keyword with optional organism/disease/tissue filters | `query: str` |
| `fetch_biosample` | Get full metadata for a known accession | `accession: str` |
| `submit_biosample` | Submit a new sample (requires AAP token) | Sample fields + env token |

### Example: Search

```bash
curl -X POST http://localhost:8000/tools/search_biosamples/call \
  -H "Content-Type: application/json" \
  -d '{"query": "human lung cancer", "organism": "Homo sapiens"}'
```

### Example: Fetch

```bash
curl -X POST http://localhost:8000/tools/fetch_biosample/call \
  -H "Content-Type: application/json" \
  -d '{"accession": "SAMEA112654119"}'
```

## Use Cases

- **Hospital research teams** — query and compare patient tissue samples across public datasets
- **Pharma companies** — find relevant disease model samples for drug target validation
- **Bio-informatics labs** — integrate BioSamples data into AI-powered analysis pipelines
- **Academic researchers** — let LLM assistants help navigate millions of public samples

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server locally
uvicorn src.server:app --reload

# Run tests
pytest tests/ -v

# Lint
ruff check src/
```

## Tech Stack

- **Python 3.11** — type hints throughout, modern async patterns
- **FastAPI** — async HTTP server with automatic OpenAPI docs
- **httpx** — async HTTP client for BioSamples API calls
- **Pydantic v2** — data validation for tool inputs and outputs
- **MCP SDK** — Model Context Protocol integration
- **Docker** — containerised deployment with non-root user
- **GitHub Actions** — CI on every push to main
