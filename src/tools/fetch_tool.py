# MCP tool: fetch_biosample — retrieves full metadata for a known accession
# Example input: {"accession": "SAMEA112654119"} (human tissue sample from EBI)
# The agent calls this after search_biosamples to get detailed metadata

from src.biosamples_client import get_sample


# Tool name registered in the MCP schema
TOOL_NAME = "fetch_biosample"

# Description shown in tool listings
TOOL_DESCRIPTION = (
    "Fetch complete metadata for a specific BioSamples accession. "
    "Returns all available fields including characteristics, organism, "
    "collection date, and geographic location. "
    "Use after search_biosamples to get full details on a sample of interest."
)

# Input schema — just needs the accession string
TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        # The BioSamples accession to look up
        "accession": {
            "type": "string",
            "description": "BioSamples accession, e.g. 'SAMEA112654119'",
        },
    },
    # Accession is the only required field
    "required": ["accession"],
}


async def run_fetch_tool(arguments: dict) -> dict:
    """Execute the fetch_biosample MCP tool for a given accession.

    Calls the BioSamples API to retrieve full metadata and returns it
    as a dict. If the accession doesn't exist, the client raises an
    HTTPStatusError which should propagate up to the MCP error handler.
    """

    # Pull the accession out of the tool arguments
    accession = arguments["accession"]

    # Fetch the full metadata from BioSamples — may raise on 404
    sample_data = await get_sample(accession)

    # Return the full metadata dict without transformation
    # The agent can decide which fields to use
    return sample_data
