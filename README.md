# biosamples-mcp

![Python 3.11](https://img.shields.io/badge/python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green) ![MCP](https://img.shields.io/badge/MCP-enabled-purple) ![Docker](https://img.shields.io/badge/docker-ready-blue) ![BioSamples API](https://img.shields.io/badge/BioSamples-EBI-orange) ![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)

A production-ready MCP server that connects AI agents to the EMBL-EBI BioSamples database — enabling intelligent biological sample search, metadata validation, and submission through a clean tool interface.

## Why This Project Matters

Biological sample metadata stored in public repositories like EMBL-EBI BioSamples is rich but difficult to access programmatically. Researchers at hospitals, pharmaceutical companies, and academic institutions spend significant time manually searching, validating, and submitting sample data through web interfaces — a process that does not scale.

This project implements the Model Context Protocol (MCP) as a structured bridge between AI agents and the BioSamples REST API. By defining explicit tool schemas with validated inputs and outputs, it allows any LLM-based system to interact with BioSamples programmatically — without hallucinations, without manual data entry, and with full traceability back to the authoritative data source.

The server is not a prototype. Two biological samples (SAMEA122005222 and SAMEA122005223) were submitted live to the EMBL-EBI BioSamples database during development, confirming end-to-end functionality against the production API.

## System Architecture

The following diagrams show how all components of the system connect and communicate. Each layer is color-coded: blue for clients, green for servers, orange for standard tools, red for AI-powered tools, purple for the intelligence layer, and gray for the external API.

---

### Diagram 1 — System Overview

![System Overview](screenshots/03_diagram_system.png)

Key points:
- Three client types connect to the server: Streamlit UI, LLM Agent (Claude Desktop), and REST clients
- Two server transports: FastAPI REST (port 8000) for HTTP clients, FastMCP stdio for Claude Desktop
- Five MCP tools handle all requests
- Two AI modules (nlp_parser + checklist_validator) power the smart tools
- All tools connect to the EMBL-EBI BioSamples REST API

---

### Diagram 2 — AI-Assisted Submission Workflow

![Submission Workflow](screenshots/04_diagram_workflow.png)

Key points:
- Step 1: User writes a plain English sample description
- Step 2: nlp_parser.py extracts organism, tissue, disease, location, and date automatically
- Step 3: checklist_validator.py checks required fields
- Step 4: If fields are missing, clarification questions are returned to the user
- Step 5: User answers are merged with extracted metadata
- Step 6: Complete record is submitted to EMBL-EBI API
- Step 7: Real BioSamples accession is returned

---

### Diagram 3 — Repository File Structure

![File Structure](screenshots/05_diagram_files.png)

Key points:
- src/ — all server logic, tools, and AI modules
- ui/ — Streamlit interface with 5 pages
- tests/ — 21 automated tests, all passing
- checklists/ — BioSamples validation JSON definitions
- Dockerfile + docker-compose.yml — container deployment
- .github/workflows/ — GitHub Actions CI pipeline

---

## Live Demo Evidence

The following samples were submitted to the EMBL-EBI BioSamples production database during development, confirming that the submission pipeline works end-to-end:

| Accession | Description | Submitted via |
|-----------|-------------|---------------|
| SAMEA122005222 | Human blood sample, Germany | submit_biosample (structured) |
| SAMEA122005223 | Human liver biopsy, London, cirrhosis | smart_submit_biosample (plain English) |

View live: https://www.ebi.ac.uk/biosamples/samples/SAMEA122005222

View live: https://www.ebi.ac.uk/biosamples/samples/SAMEA122005223

## Web Interface

The Streamlit interface provides visual access to all five MCP tools. The following screenshots show each page with a brief description of its key features.

Start the interface:

```bash
# Terminal 1 — start the MCP server
export $(cat .env) && uvicorn src.server:app --reload

# Terminal 2 — start the Streamlit UI
pip install -r requirements-ui.txt
streamlit run ui/app.py
```

Open http://localhost:8501 in your browser.

---

### Home Page

![Home Page](screenshots/01_home.png)

Key points:
- Shows live server connection status (green = online)
- Displays all 5 available tools with descriptions
- Quick demo button fetches SAMEA122005222 to verify server is connected and working

---

### Architecture Page

![Architecture Page](screenshots/02_architecture_full.png)

Key points:
- Three color-coded diagrams explain the full system
- Interactive — rendered live in the browser
- Suitable for technical presentations and interviews

---

### Search Samples

![Search Results](screenshots/06_search_results.png)

Key points:
- Keyword search across millions of BioSamples records
- Results show accession, organism, and disease
- Each accession links directly to EMBL-EBI website
- Example query buttons for quick testing

---

### Fetch Sample Details

![Fetch Sample](screenshots/07_fetch_result.png)

Key points:
- Enter any BioSamples accession to retrieve full metadata
- Two-column layout: basic info + biological attributes
- Expandable raw characteristics section
- Pre-loaded buttons for SAMEA122005222 and SAMEA122005223

---

### AI-Assisted Submission

![AI Submit Form](screenshots/08_ai_submit.png)

![AI Submit Clarification](screenshots/09_ai_submit_clarification.png)

Key points:
- Describe a sample in plain English — no forms to fill
- System automatically extracts all metadata fields
- Two checklists: default (minimum) or human_sample (strict)
- If fields are missing: targeted questions are shown
- Once complete: sample is submitted and accession returned
- Live proof: SAMEA122005222 and SAMEA122005223 were submitted this way

---

### Natural Language Search

![NL Search](screenshots/10_nl_search_results.png)

Key points:
- Search using plain English — no query syntax needed
- System shows which filters it extracted from your query
- Results include accession, organism, tissue, disease
- Example query buttons for quick testing

---

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
