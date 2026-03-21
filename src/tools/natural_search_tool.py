# MCP tool: natural_search_biosamples
# Lets users search BioSamples using plain English instead of API syntax
# Example: "human blood samples from Germany with diabetes after 2020"

from src.biosamples_client import search_samples
from src.nlp_parser import parse_sample_description

# Tool name registered in the MCP schema
TOOL_NAME = "natural_search_biosamples"

# Description shown in tool listings so agents know when to use this tool
TOOL_DESCRIPTION = (
    "Search EMBL-EBI BioSamples using a plain English query. "
    "Automatically extracts filters like organism, disease, tissue, and location. "
    "Returns structured results with accession, name, organism, disease, and tissue."
)

# JSON schema the MCP server exposes to clients
TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        # The only required field — a natural language search string
        "query": {
            "type": "string",
            "description": "Natural language query, e.g. 'Human blood samples Germany diabetes 2022'",
        },
    },
    # Query is the only required input
    "required": ["query"],
}


async def run_natural_search_tool(arguments: dict) -> dict:
    """Execute the natural_search_biosamples tool with a plain text query.

    Parses the query to extract structured filters, builds an appropriate
    BioSamples search request, and returns normalized results with the
    interpreted filters shown alongside the results for transparency.
    """

    # Extract the raw query string from the arguments
    query = arguments["query"]

    # Run the NLP parser to pull organism, tissue, disease, etc. out of the text
    parse_result = parse_sample_description(query)

    # Grab just the fields the parser found
    extracted = parse_result["extracted"]

    # Build the search query string from the most informative fields we found
    query_parts = []

    # Add organism to the text query if we identified it
    if "organism" in extracted:
        query_parts.append(extracted["organism"])

    # Add disease to the text query if we found one
    if "disease" in extracted:
        query_parts.append(extracted["disease"])

    # Add tissue type to the text query if present
    if "tissue" in extracted:
        query_parts.append(extracted["tissue"])

    # Fall back to the original query if we couldn't extract any structured fields
    search_text = " ".join(query_parts) if query_parts else query

    # Build the filter dict for structured attribute filtering in BioSamples
    filters = {}

    # Add organism filter if we recognized the organism
    if "organism" in extracted:
        filters["organism"] = extracted["organism"]

    # Add disease filter — note BioSamples uses "disease or disorder" as attribute name
    if "disease" in extracted:
        filters["disease or disorder"] = extracted["disease"]

    # Add tissue filter if we found a tissue type
    if "tissue" in extracted:
        filters["tissue"] = extracted["tissue"]

    # Call the BioSamples API with our structured query and filters
    raw_results = await search_samples(
        query=search_text,
        # Pass None instead of an empty dict so the client skips the filter params
        filters=filters if filters else None,
    )

    # Normalize each result into a clean summary dict
    normalized = []
    for sample in raw_results:
        # Pull characteristics out of the raw result
        chars = sample.get("characteristics", {})

        # Helper to safely pull the first text value from a characteristic list
        def get_char(key: str) -> str:
            """Get the first text value from a characteristics list or return empty string."""
            entries = chars.get(key, [])
            return entries[0].get("text", "") if entries else ""

        # Build the normalized result dict with the most useful fields
        normalized.append({
            "accession": sample.get("accession", ""),
            "name": sample.get("name", ""),
            # Organism can be in characteristics or at the top level
            "organism": get_char("organism"),
            # Disease uses the full attribute name BioSamples stores
            "disease": get_char("disease or disorder"),
            "tissue": get_char("tissue"),
            # Collection date is stored under this exact attribute name
            "collection_date": get_char("collection date"),
            # Geographic location uses this long attribute name in BioSamples
            "geographic_location": get_char("geographic location (country and/or sea)"),
        })

    # Return the interpreted filters alongside the results for transparency
    return {
        "tool": TOOL_NAME,
        "query_interpreted_as": extracted,
        "results_count": len(normalized),
        "results": normalized,
    }
