# MCP tool: search_biosamples — lets an AI agent search BioSamples by keyword
# Example query the agent might send: "lung cancer human 2022"
# The agent can also filter by organism, disease, or tissue type

from src.biosamples_client import search_samples


# Tool name as it appears in the MCP schema — agents reference this string
TOOL_NAME = "search_biosamples"

# Human-readable description used in the MCP tool listing
TOOL_DESCRIPTION = (
    "Search the EMBL-EBI BioSamples database by free-text query. "
    "Optionally filter by organism, disease, or tissue. "
    "Returns a list of matching samples with accession, name, organism, and disease."
)

# JSON schema the MCP server advertises — agents use this to build their inputs
TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        # Free-text search query — the most important input
        "query": {
            "type": "string",
            "description": "Free-text search query, e.g. 'lung cancer human 2022'",
        },
        # Optional filter: limit results to a specific organism
        "organism": {
            "type": "string",
            "description": "Filter by organism name, e.g. 'Homo sapiens'",
        },
        # Optional filter: limit results to a specific disease
        "disease": {
            "type": "string",
            "description": "Filter by disease, e.g. 'COVID-19'",
        },
        # Optional filter: limit results to a specific tissue type
        "tissue": {
            "type": "string",
            "description": "Filter by tissue type, e.g. 'blood'",
        },
    },
    # Only query is required — filters are optional
    "required": ["query"],
}


async def run_search_tool(arguments: dict) -> list[dict]:
    """Execute the search_biosamples MCP tool with validated arguments.

    Extracts the query and optional filters from the arguments dict,
    calls the BioSamples search API, and returns a compact list of
    result dicts with just the fields an agent needs for follow-up.
    """

    # Pull the required query string out of the arguments
    query = arguments["query"]

    # Collect optional filters into a dict — skip any that weren't provided
    filters = {}

    # Check for organism filter
    if "organism" in arguments and arguments["organism"]:
        # BioSamples uses 'organism' as the attribute name for organism filtering
        filters["organism"] = arguments["organism"]

    # Check for disease filter
    if "disease" in arguments and arguments["disease"]:
        # 'disease' maps to the disease state attribute in BioSamples
        filters["disease or disorder"] = arguments["disease"]

    # Check for tissue filter
    if "tissue" in arguments and arguments["tissue"]:
        # 'tissue' maps to the tissue attribute in BioSamples
        filters["tissue"] = arguments["tissue"]

    # Make the actual API call — pass None for filters if none were provided
    raw_results = await search_samples(
        query=query,
        filters=filters if filters else None,
    )

    # Trim each result down to just what an agent needs for follow-up queries
    trimmed_results = []
    for sample in raw_results:
        # Extract organism from characteristics if present
        characteristics = sample.get("characteristics", {})

        # Organism may be nested as a list with a 'text' key
        organism_entries = characteristics.get("organism", [])
        organism_name = organism_entries[0].get("text", "") if organism_entries else ""

        # Disease may also be nested the same way
        disease_entries = characteristics.get("disease or disorder", [])
        disease_name = disease_entries[0].get("text", "") if disease_entries else ""

        # Build a compact dict with just the key summary fields
        trimmed_results.append({
            "accession": sample.get("accession", ""),
            "name": sample.get("name", ""),
            "organism": organism_name,
            "disease": disease_name,
        })

    # Return the trimmed list — agent can pick accessions to fetch in detail
    return trimmed_results
