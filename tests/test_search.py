# Tests for the search_biosamples tool — hits the real BioSamples API
# These tests require internet access; they verify live integration behavior

import pytest
from src.biosamples_client import search_samples


@pytest.mark.asyncio
async def test_search_returns_results():
    """Verify that searching for 'human' returns at least one result.

    This is a live integration test against the BioSamples API. We expect
    a non-empty list since 'human' is a very common query term.
    """

    # Search for the most common keyword — should always return results
    results = await search_samples("human")

    # We expect at least one result for such a broad query
    assert isinstance(results, list)

    # The API should have millions of human samples
    assert len(results) > 0


@pytest.mark.asyncio
async def test_empty_query_graceful():
    """Verify that an empty query string doesn't crash the client.

    BioSamples may return results or an empty list for an empty query,
    but we should never get an unhandled exception.
    """

    # Pass an empty string — the API should handle it gracefully
    results = await search_samples("")

    # We just need it to return a list without raising
    assert isinstance(results, list)
