# biosamples-mcp

![Python 3.11](https://img.shields.io/badge/python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green) ![MCP](https://img.shields.io/badge/MCP-enabled-purple) ![Docker](https://img.shields.io/badge/docker-ready-blue) ![BioSamples API](https://img.shields.io/badge/BioSamples-EBI-orange) ![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)

A production-ready MCP server that connects AI agents to the EMBL-EBI BioSamples database — enabling intelligent biological sample search, metadata validation, and submission through a clean tool interface.

## Why This Project Matters

Biological sample metadata stored in public repositories like EMBL-EBI BioSamples is rich but difficult to access programmatically. Researchers at hospitals, pharmaceutical companies, and academic institutions spend significant time manually searching, validating, and submitting sample data through web interfaces — a process that does not scale.

This project implements the Model Context Protocol (MCP) as a structured bridge between AI agents and the BioSamples REST API. By defining explicit tool schemas with validated inputs and outputs, it allows any LLM-based system to interact with BioSamples programmatically — without hallucinations, without manual data entry, and with full traceability back to the authoritative data source.

The server is not a prototype. Two biological samples (SAMEA122005222 and SAMEA122005223) were submitted live to the EMBL-EBI BioSamples database during development, confirming end-to-end functionality against the production API.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Layer                         │
│                                                         │
│   Streamlit UI          LLM Agent        curl / API     │
│   (port 8501)       (Claude Desktop)     (direct)       │
└────────────┬───────────────┬─────────────────┬──────────┘
             │               │                 │
             └───────────────┴─────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────┐
│                    Server Layer                         │
│                                                         │
│   FastAPI REST Server          FastMCP stdio Server     │
│   (port 8000)                  (Claude Desktop)         │
│                                                         │
│   POST /tools/{name}/call      @mcp.tool() decorators   │
└─────────────────────────────────────────────────────────┘
                                    │
              ┌─────────────────────┼───────────────┐
              ▼                     ▼               ▼
┌────────────────┐   ┌─────────────────┐   ┌──────────────────┐
│  search        │   │  fetch          │   │  submit          │
│  biosamples    │   │  biosample      │   │  biosample       │
├────────────────┤   ├─────────────────┤   ├──────────────────┤
│  smart_submit  │   │  natural_search │   │                  │
│  biosample     │   │  biosamples     │   │                  │
└────────────────┘   └─────────────────┘   └──────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────┐
│                  Intelligence Layer                     │
│                                                         │
│   nlp_parser.py          checklist_validator.py         │
│   (metadata extraction   (BioSamples checklist          │
│    from plain text)       validation + clarification)   │
└─────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────┐
│              EMBL-EBI BioSamples API                    │
│                                                         │
│   GET  /biosamples/samples?text={query}   (search)      │
│   GET  /biosamples/samples/{accession}    (fetch)       │
│   POST /biosamples/samples                (submit)      │
│                                                         │
│   https://www.ebi.ac.uk/biosamples                      │
└─────────────────────────────────────────────────────────┘
```

## Live Demo Evidence

The following samples were submitted to the EMBL-EBI BioSamples production database during development, confirming that the submission pipeline works end-to-end:

| Accession | Description | Submitted via |
|-----------|-------------|---------------|
| SAMEA122005222 | Human blood sample, Germany | submit_biosample (structured) |
| SAMEA122005223 | Human liver biopsy, London, cirrhosis | smart_submit_biosample (plain English) |

View live: https://www.ebi.ac.uk/biosamples/samples/SAMEA122005222

View live: https://www.ebi.ac.uk/biosamples/samples/SAMEA122005223

## Web Interface

A professional Streamlit UI provides a visual interface for all 5 MCP tools — useful for demos, interviews, and exploring the BioSamples database without writing any code.

### Home

![Home](screenshots/home.png)

Overview of available tools and live server status.

### Search Samples

![Search](screenshots/search.png)

Keyword search across the EMBL-EBI BioSamples database with clickable accession links.

### Fetch Sample Details

![Fetch](screenshots/fetch.png)

Retrieve complete metadata for any BioSamples accession.

### AI-Assisted Submission

![AI Submit](screenshots/ai_submit.png)

Submit samples from plain English descriptions with automatic metadata extraction and checklist validation.

### Natural Language Search

![NL Search](screenshots/nl_search.png)

Query samples using conversational language — the server parses filters automatically and shows the interpretation alongside the results.

### Quick Start with UI

```bash
# Terminal 1: Start the MCP REST server
export $(cat .env) && uvicorn src.server:app --reload

# Terminal 2: Start the Streamlit UI
streamlit run ui/app.py
```

Open http://localhost:8501 in your browser.

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

## MCP Tools Reference

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `search_biosamples` | Keyword search across BioSamples | `query: str` | List of matching samples |
| `fetch_biosample` | Full metadata by accession | `accession: str` | Complete sample record |
| `submit_biosample` | Submit structured sample | metadata fields + AAP token | Assigned accession |
| `smart_submit_biosample` | Submit from plain English | `description: str` | Accession or clarification questions |
| `natural_search_biosamples` | NL query to structured search | `query: str` | Filtered results + interpretation |

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

## AI-Assisted Submission Workflow

```
User input (plain English)
"Human liver biopsy London 2023 with cirrhosis"
              │
              ▼
       nlp_parser.py
  extracts: organism, tissue,
   disease, location, date
              │
              ▼
  checklist_validator.py
  checks required fields against
       selected checklist
              │
         ┌────┴────┐
         │         │
         ▼         ▼
      Missing    All fields
       fields     present
         │         │
         ▼         ▼
      Return    submit_sample()
     questions  to EMBL-EBI API
      to user         │
         │            ▼
         ▼      Returns accession
       User       SAMEA......
      answers
         │
         ▼
  Merge + revalidate
         │
         ▼
   submit_sample()
```

## Use Cases

Clinical research departments can use this server to programmatically search public sample datasets for cohort comparisons, reducing manual database queries and enabling AI-assisted literature-linked sample discovery.

Drug development teams can integrate this MCP server into their data pipelines to find relevant disease model samples, validate sample metadata quality, and submit new experimental samples to the global repository — all through a standardised AI tool interface.

Research groups can connect LLM-based analysis assistants directly to BioSamples data without building custom API integrations. The MCP tool interface provides deterministic, hallucination-free access to authoritative biological data.

This project was independently developed as a working implementation of the EMBL-EBI GSoC 2026 project idea "Expose BioSamples Submission and Search Capabilities as MCP Tools for AI-Assisted Metadata Interaction" (Mentor: Dipayan Gupta). Reference: https://www.ebi.ac.uk/about/events/gsoc/

## Roadmap

The current implementation covers the core submission and search capabilities described in the project specification. Planned extensions include integration with the live BioSamples checklist API to replace the static JSON files, multi-turn conversational session management for complex submission workflows, rate-limit-aware caching for high-volume queries, and expansion to additional EMBL-EBI resources including ENA and ArrayExpress.

## Tech Stack

- **Python 3.11** — type hints throughout, modern async patterns
- **FastAPI** — async HTTP server with automatic OpenAPI docs
- **httpx** — async HTTP client for BioSamples API calls
- **Pydantic v2** — data validation for tool inputs and outputs
- **MCP SDK** — Model Context Protocol integration
- **Docker** — containerised deployment with non-root user
- **GitHub Actions** — CI on every push to main

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
