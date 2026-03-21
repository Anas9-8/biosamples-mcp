# Tests for the submit_biosample tool — validates input models and mocks the HTTP call
# We don't make real submissions in tests — that would create junk records in BioSamples

import pytest
from unittest.mock import AsyncMock, patch
from pydantic import ValidationError
from src.models.sample import SubmitSampleRequest
from src.tools.submit_tool import run_submit_tool


def test_valid_payload_passes_validation():
    """Verify that a complete SubmitSampleRequest validates without errors.

    Creates a realistic blood sample payload mimicking a clinical trial
    submission and confirms Pydantic accepts all the fields.
    """

    # Build a realistic human blood sample from a hypothetical clinical trial
    request = SubmitSampleRequest(
        name="ClinicalTrial_BloodSample_001",
        organism="Homo sapiens",
        taxon_id=9606,
        tissue="blood",
        disease="healthy",
        collection_date="2024-06-15",
        geographic_location="United Kingdom",
        additional_metadata={"treatment": "placebo", "age": "45"},
    )

    # If we got here without an exception, validation passed
    assert request.name == "ClinicalTrial_BloodSample_001"

    # Verify a few other fields to make sure they were stored correctly
    assert request.taxon_id == 9606
    assert request.organism == "Homo sapiens"


def test_missing_fields_raises_error():
    """Verify that an incomplete SubmitSampleRequest raises a ValidationError.

    Omitting required fields like organism should cause Pydantic to raise
    a ValidationError — this protects against partial submissions.
    """

    # Deliberately omit several required fields
    with pytest.raises(ValidationError):
        # organism, taxon_id, tissue, disease, collection_date, geographic_location are all missing
        SubmitSampleRequest(name="incomplete_sample")


@pytest.mark.asyncio
async def test_submit_calls_api_with_token(monkeypatch):
    """Verify that run_submit_tool calls the BioSamples API when a token is set.

    Uses a mock for the HTTP client so we don't make real API calls.
    Checks that the tool returns a dict with accession and status fields.
    """

    # Set a fake token in the environment so the tool doesn't refuse to proceed
    monkeypatch.setenv("AAP_TOKEN", "fake-test-token-123")

    # Mock the submit_sample client function to return a fake accession
    with patch("src.tools.submit_tool.submit_sample", new_callable=AsyncMock) as mock_submit:
        # Set the mock to return a plausible accession string
        mock_submit.return_value = "SAMEA999999"

        # Call the tool with a full valid payload
        result = await run_submit_tool({
            "name": "TestSample",
            "organism": "Homo sapiens",
            "taxon_id": 9606,
            "tissue": "blood",
            "disease": "healthy",
            "collection_date": "2024-01-01",
            "geographic_location": "United Kingdom",
        })

    # The result should include the accession and a submitted status
    assert result["accession"] == "SAMEA999999"
    assert result["status"] == "submitted"
