# BioSamples REST API client — wraps the EMBL-EBI BioSamples HTTP API
# Real accessions used throughout for testing: SAMEA112654119 (human tissue),
# SAMN39198001 (pathogen), SAMEA7997453 (COVID-19 related sample)

from typing import Optional

import httpx

# Base URL for the public BioSamples API
BIOSAMPLES_BASE_URL = "https://www.ebi.ac.uk/biosamples"


async def search_samples(
    query: str,
    filters: Optional[dict] = None,
    page_size: int = 10
) -> list[dict]:
    """Search BioSamples by free-text query with optional attribute filters.

    Hits the BioSamples search endpoint and returns a flat list of sample
    summary dicts. Each dict has basic fields like accession, name, organism.
    Filters are passed as attr:field:value pairs e.g. organism:Homo sapiens.
    """

    # Build the base query params with search text and result count
    params = {
        "text": query,
        "size": page_size,
    }

    # If caller provided filters (organism, disease, tissue), append them
    if filters:
        # BioSamples API uses repeated 'filter' params for attribute filtering
        filter_values = []
        for field, value in filters.items():
            # Format follows the API spec: attr:FieldName:value
            filter_values.append(f"attr:{field}:{value}")
        # httpx accepts list values for repeated query params
        params["filter"] = filter_values

    # Use async httpx so we don't block the event loop during the HTTP call
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Fire the GET request to the samples search endpoint
        response = await client.get(
            f"{BIOSAMPLES_BASE_URL}/samples",
            params=params,
        )
        # Raise immediately if the API returned an error status
        response.raise_for_status()

    # Parse the JSON body — BioSamples uses HAL format with _embedded
    data = response.json()

    # Pull out the samples list from the HAL envelope, default to empty list
    samples = data.get("_embedded", {}).get("samples", [])

    # Return the raw list of sample dicts as-is for now
    return samples


async def get_sample(accession: str) -> dict:
    """Fetch full metadata for a single BioSamples accession.

    Takes an accession like SAMEA112654119 and returns the complete JSON
    metadata dict from BioSamples. Raises a clear HTTPError on 404 so
    callers know the accession doesn't exist rather than getting a cryptic error.
    """

    # Construct the direct accession URL
    url = f"{BIOSAMPLES_BASE_URL}/samples/{accession}"

    # Async client with a reasonable timeout for large metadata responses
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Make the GET request for this specific accession
        response = await client.get(url)

        # If accession wasn't found, raise with a human-readable message
        if response.status_code == 404:
            raise httpx.HTTPStatusError(
                f"Sample {accession} not found in BioSamples",
                request=response.request,
                response=response,
            )

        # Any other non-2xx status should also bubble up clearly
        response.raise_for_status()

    # Return the full metadata dict
    return response.json()


async def submit_sample(metadata: dict, token: str) -> str:
    """Submit a new sample to BioSamples and return the assigned accession.

    Sends a POST request with Bearer token auth and the sample metadata as
    JSON. Returns the new accession string (e.g. SAMEA...) from the response.
    Requires a valid AAP token — get one from https://aai.ebi.ac.uk.
    """

    # Send as plain JSON but tell the API we can receive HAL+JSON back
    # Using application/hal+json as Content-Type causes a 415 — the API only accepts application/json
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/hal+json",
    }

    # Post the metadata to the BioSamples submission endpoint
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Send the POST with JSON body and auth header
        response = await client.post(
            f"{BIOSAMPLES_BASE_URL}/samples",
            json=metadata,
            headers=headers,
        )
        # Raise on any HTTP error so callers get a clear failure signal
        response.raise_for_status()

    # Parse the response and extract the assigned accession
    result = response.json()

    # The accession is at the top level of the response under 'accession'
    accession = result.get("accession", "")

    # Return just the accession string — callers can store it for reference
    return accession
