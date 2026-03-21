# MCP server for BioSamples — exposes three AI-callable tools via FastAPI
# Implements the Model Context Protocol so LLM agents can query BioSamples
# Start with: uvicorn src.server:app --reload

from fastapi import FastAPI, HTTPException
from src.tools.search_tool import TOOL_NAME as SEARCH_NAME, TOOL_DESCRIPTION as SEARCH_DESC, TOOL_SCHEMA as SEARCH_SCHEMA, run_search_tool
from src.tools.fetch_tool import TOOL_NAME as FETCH_NAME, TOOL_DESCRIPTION as FETCH_DESC, TOOL_SCHEMA as FETCH_SCHEMA, run_fetch_tool
from src.tools.submit_tool import TOOL_NAME as SUBMIT_NAME, TOOL_DESCRIPTION as SUBMIT_DESC, TOOL_SCHEMA as SUBMIT_SCHEMA, run_submit_tool

# Create the FastAPI application instance
app = FastAPI(
    title="BioSamples MCP Server",
    description="MCP server exposing EMBL-EBI BioSamples API as AI-callable tools",
    version="1.0.0",
)

# Register all three tools in a list so we can iterate over them
REGISTERED_TOOLS = [
    {
        # Search tool — lets agents search by keyword and filters
        "name": SEARCH_NAME,
        "description": SEARCH_DESC,
        "schema": SEARCH_SCHEMA,
        "handler": run_search_tool,
    },
    {
        # Fetch tool — retrieves full metadata for a known accession
        "name": FETCH_NAME,
        "description": FETCH_DESC,
        "schema": FETCH_SCHEMA,
        "handler": run_fetch_tool,
    },
    {
        # Submit tool — posts a new sample to BioSamples
        "name": SUBMIT_NAME,
        "description": SUBMIT_DESC,
        "schema": SUBMIT_SCHEMA,
        "handler": run_submit_tool,
    },
]

# Build a name-to-handler lookup for fast routing in the call endpoint
TOOL_HANDLERS = {tool["name"]: tool["handler"] for tool in REGISTERED_TOOLS}


@app.get("/health")
async def health_check():
    """Return server health status — used by Docker healthchecks and load balancers."""
    # Return a simple ok status with the current server version
    return {"status": "ok", "version": "1.0.0"}


@app.get("/tools")
async def list_tools():
    """Return the list of available MCP tools with names and descriptions."""
    # Build a slim list — agents use this to discover what tools exist
    return [
        {"name": tool["name"], "description": tool["description"]}
        for tool in REGISTERED_TOOLS
    ]


@app.post("/tools/{tool_name}/call")
async def call_tool(tool_name: str, arguments: dict):
    """Dispatch a tool call by name with the given arguments dict.

    Looks up the tool handler, runs it with the provided arguments, and
    returns the result. Returns 404 if the tool name isn't registered.
    """

    # Check if the requested tool name exists in our registry
    if tool_name not in TOOL_HANDLERS:
        # Return a clear 404 with the unknown name so agents can debug
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    # Get the handler function for this tool
    handler = TOOL_HANDLERS[tool_name]

    # Await the async handler with the caller's arguments
    result = await handler(arguments)

    # Wrap the result in a standard response envelope
    return {"tool": tool_name, "result": result}
