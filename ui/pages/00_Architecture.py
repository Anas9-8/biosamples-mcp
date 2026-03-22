# Architecture page — shows how the BioSamples MCP server is structured
# Uses 00_ prefix so it appears first in the Streamlit sidebar

import sys
import os

# Add the project root so imports from ui/ resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st

# Page configuration — wide layout gives the diagram more room
st.set_page_config(
    page_title="System Architecture — BioSamples MCP",
    page_icon="",
    layout="wide",
)

# Page heading
st.title("System Architecture")

# One-sentence subtitle describing the diagram's scope
st.write(
    "How the BioSamples MCP server connects AI agents "
    "to the EMBL-EBI BioSamples database."
)

# Horizontal divider below the header
st.divider()

# --- Overview section ---

# Section heading
st.subheader("Overview")

# Two sentences describing the architecture at a high level
st.write(
    "The server exposes five MCP tools through two transports: "
    "a FastAPI REST server on port 8000 for HTTP clients "
    "(Streamlit UI, curl, Docker containers) and a FastMCP "
    "stdio server for Claude Desktop. "
    "Two of the tools use an embedded NLP layer to extract "
    "structured metadata from plain English text before "
    "forwarding requests to the EMBL-EBI BioSamples API."
)

# --- System Diagram section ---

# Section heading
st.subheader("System Diagram")

# Render the architecture as a graphviz directed graph
# graphviz_chart is built into Streamlit — no extra package needed
st.graphviz_chart("""
digraph {
  rankdir=TB
  node [shape=box, style=rounded]

  UI      [label="Streamlit UI\\n(port 8501)"]
  Agent   [label="LLM Agent\\n(Claude Desktop)"]
  APIcurl [label="Direct API\\n(curl / REST)"]

  REST [label="FastAPI REST Server\\n(port 8000)"]
  MCP  [label="FastMCP stdio Server\\n(Claude Desktop)"]

  Search [label="search_biosamples"]
  Fetch  [label="fetch_biosample"]
  Submit [label="submit_biosample"]
  Smart  [label="smart_submit_biosample"]
  NL     [label="natural_search_biosamples"]

  NLP       [label="nlp_parser.py\\n(text extraction)"]
  Validator [label="checklist_validator.py\\n(validation)"]

  BioSamples [label="EMBL-EBI BioSamples API\\nhttps://www.ebi.ac.uk/biosamples"]

  UI      -> REST
  Agent   -> MCP
  APIcurl -> REST

  REST -> Search
  REST -> Fetch
  REST -> Submit
  REST -> Smart
  REST -> NL

  MCP -> Search
  MCP -> Fetch
  MCP -> Submit
  MCP -> Smart
  MCP -> NL

  Smart -> NLP
  Smart -> Validator
  NL    -> NLP

  Search -> BioSamples
  Fetch  -> BioSamples
  Submit -> BioSamples
  Smart  -> BioSamples
  NL     -> BioSamples
}
""")

# --- Component Descriptions section ---

# Section heading
st.subheader("Component Descriptions")

# Component table — one row per key module
st.markdown("""
| Component | File | Purpose |
|-----------|------|---------|
| REST Server | `src/server.py` | HTTP API for curl, Docker, Streamlit |
| MCP Server | `src/mcp_server.py` | stdio server for Claude Desktop |
| BioSamples Client | `src/biosamples_client.py` | All EMBL-EBI API calls |
| NLP Parser | `src/nlp_parser.py` | Extract metadata from plain text |
| Checklist Validator | `src/checklist_validator.py` | Validate against BioSamples checklists |
| Streamlit UI | `ui/app.py` | Visual interface for demos |
""")

# --- Submission Workflow section ---

# Section heading
st.subheader("AI-Assisted Submission Workflow")

# Numbered list showing each step of the smart_submit flow
st.markdown("""
1. User describes sample in plain English
2. `nlp_parser.py` extracts organism, tissue, disease, location, date
3. `checklist_validator.py` checks required fields against the selected checklist
4. If fields are missing: clarification questions are returned to the user
5. User provides answers
6. System merges answers and revalidates
7. `submit_sample()` sends the completed record to the EMBL-EBI BioSamples API
8. Real accession is returned (e.g. SAMEA122005222)
""")

# --- Live Evidence section ---

# Section heading
st.subheader("Live Evidence")

# One sentence introducing the confirmed accessions
st.write(
    "The following samples were submitted to the EMBL-EBI BioSamples "
    "production database during development, confirming end-to-end functionality:"
)

# Link to the first confirmed accession
st.markdown(
    "**SAMEA122005222** — Human blood sample, Germany  "
    "[View on BioSamples](https://www.ebi.ac.uk/biosamples/samples/SAMEA122005222)"
)

# Link to the second confirmed accession
st.markdown(
    "**SAMEA122005223** — Human liver biopsy, London, cirrhosis  "
    "[View on BioSamples](https://www.ebi.ac.uk/biosamples/samples/SAMEA122005223)"
)
