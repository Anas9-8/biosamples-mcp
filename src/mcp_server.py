# Real MCP server using FastMCP — this is what Claude Desktop and other MCP
# clients actually connect to. Communicates over stdio, not HTTP.
# Run it with: python -m src.mcp_server
# Add it to Claude Desktop by pointing to this file in claude_desktop_config.json

from typing import Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load .env so AAP_TOKEN is available when the submit tool runs
load_dotenv()

from src.tools.fetch_tool import run_fetch_tool

# Import the tool logic we already wrote — no need to duplicate it
from src.tools.search_tool import run_search_tool
from src.tools.submit_tool import run_submit_tool

# Create the FastMCP server instance — the name shows up in Claude Desktop
mcp = FastMCP("biosamples-mcp")


@mcp.tool()
async def search_biosamples(
    query: str,
    organism: Optional[str] = None,
    disease: Optional[str] = None,
    tissue: Optional[str] = None,
) -> list:
    """Search the EMBL-EBI BioSamples database by free-text query.

    Optionally filter by organism, disease, or tissue type.
    Returns a list of matching samples with accession, name, organism, and disease.
    Example: search_biosamples('lung cancer human 2022', organism='Homo sapiens')
    """

    # Build the arguments dict the existing tool handler expects
    arguments = {"query": query}

    # Only include filters if the caller actually passed them
    if organism:
        arguments["organism"] = organism
    if disease:
        arguments["disease"] = disease
    if tissue:
        arguments["tissue"] = tissue

    # Delegate to the tool handler — keeps all business logic in one place
    return await run_search_tool(arguments)


@mcp.tool()
async def fetch_biosample(accession: str) -> dict:
    """Fetch full metadata for a specific BioSamples accession.

    Returns all available fields: characteristics, organism, collection date,
    geographic location, and more. Use after search_biosamples to get details
    on a sample of interest. Example accession: SAMEA112654119
    """

    # Pass the accession through to the fetch handler
    return await run_fetch_tool({"accession": accession})


@mcp.tool()
async def submit_biosample(
    name: str,
    organism: str,
    taxon_id: int,
    tissue: str,
    disease: str,
    collection_date: str,
    geographic_location: str,
    additional_metadata: Optional[dict] = None,
) -> dict:
    """Submit a new biological sample to the EMBL-EBI BioSamples archive.

    Requires AAP_TOKEN to be set in the environment before calling.
    Returns the assigned BioSamples accession on success.
    Example: submit a human blood sample from a clinical trial.
    """

    # Build the arguments dict — submit handler expects all fields present
    arguments = {
        "name": name,
        "organism": organism,
        "taxon_id": taxon_id,
        "tissue": tissue,
        "disease": disease,
        "collection_date": collection_date,
        "geographic_location": geographic_location,
    }

    # Only add additional_metadata if the caller provided it
    if additional_metadata:
        arguments["additional_metadata"] = additional_metadata

    # Delegate to the submit handler which reads AAP_TOKEN from the environment
    return await run_submit_tool(arguments)


# When run directly, start the stdio transport that MCP clients connect to
if __name__ == "__main__":
    # mcp.run() defaults to stdio — the right transport for Claude Desktop
    mcp.run()
