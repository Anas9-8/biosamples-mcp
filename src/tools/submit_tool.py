# MCP tool: submit_biosample — submits a new sample to BioSamples
# Example use case: a hospital submitting human blood samples from a clinical trial
# Requires a valid AAP Bearer token — the agent must include it in the environment

import os

from src.biosamples_client import submit_sample
from src.models.sample import SubmitSampleRequest

# Tool name as registered in the MCP schema
TOOL_NAME = "submit_biosample"

# Description of what this tool does for tool listings
TOOL_DESCRIPTION = (
    "Submit a new biological sample to the EMBL-EBI BioSamples archive. "
    "Requires a valid AAP Bearer token set as the AAP_TOKEN environment variable. "
    "Returns the assigned BioSamples accession on success."
)

# Input JSON schema — mirrors the SubmitSampleRequest model fields
TOOL_SCHEMA = {
    "type": "object",
    "properties": {
        # Sample name — should be descriptive
        "name": {
            "type": "string",
            "description": "Descriptive name for the sample",
        },
        # Scientific organism name
        "organism": {
            "type": "string",
            "description": "Scientific organism name, e.g. 'Homo sapiens'",
        },
        # NCBI Taxonomy ID
        "taxon_id": {
            "type": "integer",
            "description": "NCBI Taxonomy ID, e.g. 9606 for Homo sapiens",
        },
        # Tissue of origin
        "tissue": {
            "type": "string",
            "description": "Tissue type, e.g. 'blood', 'lung'",
        },
        # Disease association
        "disease": {
            "type": "string",
            "description": "Disease association or 'healthy'",
        },
        # ISO collection date
        "collection_date": {
            "type": "string",
            "description": "Collection date in YYYY-MM-DD format",
        },
        # Geographic collection location
        "geographic_location": {
            "type": "string",
            "description": "Country or region of collection, e.g. 'United Kingdom'",
        },
        # Any extra metadata attributes
        "additional_metadata": {
            "type": "object",
            "description": "Optional extra attributes as key-value pairs",
        },
    },
    # All core fields are required for a valid BioSamples submission
    "required": [
        "name", "organism", "taxon_id", "tissue",
        "disease", "collection_date", "geographic_location"
    ],
}


async def run_submit_tool(arguments: dict) -> dict:
    """Execute the submit_biosample MCP tool with validated sample data.

    Validates the input against SubmitSampleRequest, reads the AAP token
    from the environment, builds the BioSamples submission payload, and
    posts it. Returns the new accession and a status string.
    """

    # Validate all fields using the Pydantic model — raises on bad input
    request = SubmitSampleRequest(**arguments)

    # Read the auth token from the environment — never accept it as tool input
    token = os.environ.get("AAP_TOKEN", "")

    # Refuse to proceed if no token is configured
    if not token:
        raise ValueError(
            "AAP_TOKEN environment variable is not set. "
            "Set it to your EMBL-EBI AAP Bearer token before submitting."
        )

    # Build the BioSamples JSON submission format
    # BioSamples expects characteristics as lists of {text} objects
    payload = {
        # Sample display name
        "name": request.name,
        # Characteristics dict — each value is a list of text objects
        "characteristics": {
            # Organism with NCBI taxonomy reference
            "organism": [{"text": request.organism, "ontologyTerms": [f"http://purl.obolibrary.org/obo/NCBITaxon_{request.taxon_id}"]}],
            # Tissue attribute
            "tissue": [{"text": request.tissue}],
            # Disease attribute
            "disease or disorder": [{"text": request.disease}],
            # Collection date as a text attribute
            "collection date": [{"text": request.collection_date}],
            # Geographic location
            "geographic location (country and/or sea)": [{"text": request.geographic_location}],
        },
    }

    # Merge any additional metadata the caller provided
    if request.additional_metadata:
        for key, value in request.additional_metadata.items():
            # Each value gets wrapped in the same list-of-text format
            payload["characteristics"][key] = [{"text": str(value)}]

    # Call the client to POST the payload and get back the accession
    accession = await submit_sample(payload, token)

    # Return a structured result with the accession and a status flag
    return {
        "accession": accession,
        "status": "submitted",
    }
