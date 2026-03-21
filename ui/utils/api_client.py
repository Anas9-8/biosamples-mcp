# HTTP client that calls the local BioSamples MCP REST server at localhost:8000
# All functions here are thin wrappers — they just POST to the right endpoint
# and return the JSON result dict. If the server is down they return a clear error.

import requests

# Base URL for the local REST server — must match where uvicorn is listening
SERVER_BASE = "http://localhost:8000"

# Timeout in seconds for all HTTP calls — long enough for BioSamples API round-trips
REQUEST_TIMEOUT = 30


def _post_tool(tool_name: str, arguments: dict) -> dict:
    """POST arguments to /tools/{tool_name}/call and return the result dict.

    This is the single internal helper all public functions use. Returns a dict
    with either a 'result' key on success or an 'error' key on failure.
    """

    # Build the full endpoint URL from the tool name
    url = f"{SERVER_BASE}/tools/{tool_name}/call"

    # Wrap the call in a try block so network errors never crash the UI
    try:
        # Send the POST request with the arguments as JSON body
        response = requests.post(url, json=arguments, timeout=REQUEST_TIMEOUT)

        # If the server returned a non-2xx status, build a descriptive error dict
        if not response.ok:
            # Include the status code so the UI can show a meaningful message
            return {"error": f"Server returned {response.status_code}: {response.text}"}

        # Parse the JSON response body and return it directly
        return response.json()

    except requests.exceptions.ConnectionError:
        # Server is not running — give the user the exact command to fix it
        return {"error": "Server not running. Start with: uvicorn src.server:app --reload"}

    except requests.exceptions.Timeout:
        # BioSamples API took too long — transient issue, user can retry
        return {"error": "Request timed out. The BioSamples API may be slow. Try again."}

    except Exception as exc:
        # Catch anything else so the UI never shows an unhandled Python traceback
        return {"error": f"Unexpected error: {str(exc)}"}


def check_server_health() -> bool:
    """GET /health and return True if the server responds with status ok."""

    # Try a simple GET to the health endpoint — no body needed
    try:
        # Short timeout — health checks should be near-instant
        response = requests.get(f"{SERVER_BASE}/health", timeout=5)

        # Return True only if the server said ok
        return response.ok and response.json().get("status") == "ok"

    except Exception:
        # Any error means the server is not reachable
        return False


def search_samples(query: str, organism: str = "", disease: str = "", tissue: str = "") -> dict:
    """Call POST /tools/search_biosamples/call and return the result dict."""

    # Build the base arguments with just the required query string
    arguments = {"query": query}

    # Only add optional filters if the caller provided non-empty strings
    if organism:
        arguments["organism"] = organism
    if disease:
        arguments["disease"] = disease
    if tissue:
        arguments["tissue"] = tissue

    # Delegate to the shared POST helper
    return _post_tool("search_biosamples", arguments)


def fetch_sample(accession: str) -> dict:
    """Call POST /tools/fetch_biosample/call and return the full sample metadata."""

    # The fetch tool only needs the accession string
    return _post_tool("fetch_biosample", {"accession": accession})


def submit_sample(metadata: dict) -> dict:
    """Call POST /tools/submit_biosample/call with structured metadata and return result."""

    # Pass the metadata dict directly as the arguments body
    return _post_tool("submit_biosample", metadata)


def smart_submit(description: str, checklist: str = "default", clarifications: dict = None) -> dict:
    """Call POST /tools/smart_submit_biosample/call with a plain-text description."""

    # Start with the required description and checklist fields
    arguments = {"description": description, "checklist": checklist}

    # Only include clarifications if the caller provided answers to questions
    if clarifications:
        arguments["clarifications"] = clarifications

    # Delegate to the shared POST helper
    return _post_tool("smart_submit_biosample", arguments)


def natural_search(query: str) -> dict:
    """Call POST /tools/natural_search_biosamples/call and return structured results."""

    # The natural search tool only needs the raw query string
    return _post_tool("natural_search_biosamples", {"query": query})
