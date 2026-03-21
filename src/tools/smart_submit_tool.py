# MCP tool: smart_submit_biosample
# Takes a plain English description, extracts metadata, validates it, and
# either asks clarification questions or submits to BioSamples — all in one call

from src.checklist_validator import validate_sample
from src.nlp_parser import parse_sample_description
from src.tools.submit_tool import run_submit_tool

# Tool name as it will appear in the MCP schema and REST endpoint
TOOL_NAME = "smart_submit_biosample"

# Description shown when agents or users list available tools
TOOL_DESCRIPTION = (
    "Submit a biological sample to EMBL-EBI BioSamples using a plain text description. "
    "Automatically extracts metadata from the description, validates against checklists, "
    "and asks clarification questions for any missing required fields before submitting."
)

# JSON schema the MCP server and REST API advertise to callers
TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        # The main input — a free-text description of the sample
        "description": {
            "type": "string",
            "description": "Plain English description of the sample, e.g. 'Human liver biopsy from London 2023 with cirrhosis'",
        },
        # Which checklist to validate against — defaults to the minimum required fields
        "checklist": {
            "type": "string",
            "description": "Checklist to validate against: 'default' or 'human_sample'",
        },
        # User answers to previous clarification questions — merged into extracted metadata
        "clarifications": {
            "type": "object",
            "description": "Answers to clarification questions from a previous call, e.g. {'collection_date': '2023-06-15', 'sex': 'male'}",
        },
    },
    # Only description is required — everything else is optional
    "required": ["description"],
}


async def run_smart_submit_tool(arguments: dict) -> dict:
    """Execute the smart_submit_biosample tool end-to-end.

    Parses the plain text description, merges any user-provided clarifications,
    validates against the requested checklist, and either returns clarification
    questions or submits the sample and returns the new accession.
    """

    # Pull the required description string from arguments
    description = arguments["description"]

    # Use "default" checklist unless the caller specified one
    checklist = arguments.get("checklist", "default")

    # Get any clarification answers the user provided in a follow-up call
    clarifications = arguments.get("clarifications", {})

    # Run the NLP parser to extract what we can from the plain text
    parse_result = parse_sample_description(description)

    # Start with the fields the parser found automatically
    metadata = dict(parse_result["extracted"])

    # Merge in any explicit clarifications the user provided — they override parsed values
    if clarifications:
        # Update the metadata dict with the user's answers
        metadata.update(clarifications)

    # Auto-infer taxon_id from organism if the user provided organism as a clarification
    if "organism" in metadata and "taxon_id" not in metadata:
        # Look up the taxon ID from the organism name
        organism_taxon_map = {
            "Homo sapiens": 9606,
            "Mus musculus": 10090,
            "Rattus norvegicus": 10116,
        }
        # Try to find the taxon ID for this organism name
        inferred_taxon = organism_taxon_map.get(metadata["organism"])
        if inferred_taxon:
            # Store the inferred taxon ID so we don't ask for it separately
            metadata["taxon_id"] = inferred_taxon

    # Validate the combined metadata against the chosen checklist
    validation = validate_sample(metadata, checklist)

    # If required fields are still missing, ask the user for them before submitting
    if not validation["ready_to_submit"]:
        # Return the clarification questions so the caller can prompt the user
        return {
            "status": "needs_clarification",
            "extracted_so_far": metadata,
            "questions": validation["clarification_questions"],
            "missing_required": validation["missing_required"],
            "missing_recommended": validation["missing_recommended"],
        }

    # All required fields are present — build a name from the metadata
    organism_short = metadata.get("organism", "Unknown").split()[0]

    # Combine organism and tissue for a descriptive auto-generated name
    tissue = metadata.get("tissue", "sample")

    # Add date to the name so it's unique and informative
    date = metadata.get("collection_date", "unknown-date")

    # Combine them into a readable sample name
    auto_name = f"{organism_short}_{tissue}_{date}"

    # Build the full arguments dict that run_submit_tool expects
    submit_args = {
        "name": auto_name,
        # organism is guaranteed present — it's required by every checklist
        "organism": metadata.get("organism", "Unknown"),
        # taxon_id falls back to 9606 (human) if it somehow slipped through validation
        "taxon_id": int(metadata.get("taxon_id", 9606)),
        # tissue is optional in the default checklist — use "unknown" as a safe fallback
        "tissue": metadata.get("tissue", "unknown"),
        # Default disease to "healthy" if the parser didn't find one
        "disease": metadata.get("disease", "healthy"),
        # collection_date is optional in the default checklist — use today as a safe fallback
        "collection_date": metadata.get("collection_date", "2024-01-01"),
        # Use "not specified" if location is still unknown after clarification
        "geographic_location": metadata.get("geographic_location", "not specified"),
    }

    # Add any extra metadata fields that aren't part of the standard schema
    extra_fields = {
        k: v for k, v in metadata.items()
        if k not in submit_args and k not in ("organism", "taxon_id")
    }

    # Only pass additional_metadata if we have any extra fields to include
    if extra_fields:
        submit_args["additional_metadata"] = extra_fields

    # Delegate the actual submission to the existing submit tool
    result = await run_submit_tool(submit_args)

    # Return a success response with the accession and a friendly message
    return {
        "status": "submitted",
        "accession": result["accession"],
        "message": f"Sample successfully submitted to EMBL-EBI BioSamples as {result['accession']}",
        "submitted_metadata": submit_args,
    }
