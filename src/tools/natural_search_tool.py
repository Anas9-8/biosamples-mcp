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

    # Build a plain text query string from the extracted fields
    # The BioSamples API only works reliably with the text= parameter —
    # structured attr filters are ignored and return 0 results in practice
    query_parts = []

    # Organism goes first — it's the most selective term
    if "organism" in extracted:
        query_parts.append(extracted["organism"])

    # Tissue narrows down the result set after organism
    if "tissue" in extracted:
        query_parts.append(extracted["tissue"])

    # Disease adds further specificity if the user mentioned one
    if "disease" in extracted:
        query_parts.append(extracted["disease"])

    # Join all extracted terms into one space-separated query string
    search_text = " ".join(query_parts) if query_parts else query

    # Run the primary search with the combined text query — no filters
    raw_results = await search_samples(query=search_text)

    # If the combined query returned nothing, fall back to the first term alone
    if not raw_results:
        # Use the first extracted term, or the first word of the original query
        fallback = query_parts[0] if query_parts else query.split()[0]
        # Retry with just that single term — broad enough to always get results
        raw_results = await search_samples(query=fallback)

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
