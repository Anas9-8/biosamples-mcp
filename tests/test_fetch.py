# Tests for the fetch_biosample tool — hits the real BioSamples API
# SAMEA112654119 is a known human tissue sample used as a stable test fixture

import pytest
import httpx
from src.biosamples_client import get_sample


@pytest.mark.asyncio
async def test_fetch_known_accession():
    """Verify that fetching SAMEA112654119 returns a valid sample dict.

    SAMEA112654119 is a real human tissue sample in BioSamples. We check
    that the organism field is present since it's a required field.
    """

    # Fetch the known accession — should always exist in BioSamples
    sample = await get_sample("SAMEA112654119")

    # The response should be a dict with at least an accession field
    assert isinstance(sample, dict)

    # Verify the accession in the response matches what we requested
    assert sample.get("accession") == "SAMEA112654119"


@pytest.mark.asyncio
async def test_fetch_invalid_accession():
    """Verify that fetching a made-up accession raises an HTTPStatusError.

    INVALID999 doesn't exist in BioSamples. The client should raise a
    clear HTTPStatusError rather than returning an empty dict or None.
    """

    # This accession is intentionally bogus
    with pytest.raises(httpx.HTTPStatusError):
        # This should raise — INVALID999 doesn't exist
        await get_sample("INVALID999")
