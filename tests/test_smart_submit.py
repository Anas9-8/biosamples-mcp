# Tests for the smart_submit_biosample tool
# Covers the clarification flow, the clarification → submit flow, and mocked submission

import pytest
from unittest.mock import AsyncMock, patch

from src.tools.smart_submit_tool import run_smart_submit_tool


@pytest.mark.asyncio
async def test_incomplete_description_returns_clarification():
    """Verify that a description missing required fields returns clarification questions.

    A description with no year (collection_date) should trigger the clarification
    workflow since collection_date is required by the default checklist only for
    the human_sample checklist. This uses the human_sample checklist to be stricter.
    """

    # A description that has organism and tissue but no date — human_sample requires date
    result = await run_smart_submit_tool({
        "description": "Human liver sample from London",
        "checklist": "human_sample",
    })

    # The tool should ask for more info rather than submitting
    assert result["status"] == "needs_clarification"

    # There should be at least one question about collection date
    assert len(result["questions"]) > 0

    # The extracted fields so far should include organism
    assert result["extracted_so_far"]["organism"] == "Homo sapiens"


@pytest.mark.asyncio
async def test_clarifications_fill_missing_fields():
    """Verify that providing clarifications moves the workflow toward submission.

    After getting clarification questions, the user provides the missing date
    and the validator should now find the human_sample checklist satisfied.
    We mock the actual submission so we don't hit the real API.
    """

    # Mock run_submit_tool so we don't need a real AAP token in tests
    with patch("src.tools.smart_submit_tool.run_submit_tool", new_callable=AsyncMock) as mock_submit:
        # Return a fake accession so the test doesn't need real credentials
        mock_submit.return_value = {"accession": "SAMEA999001", "status": "submitted"}

        # Call with description and the clarification answers for missing fields
        result = await run_smart_submit_tool({
            "description": "Human liver sample from London",
            "checklist": "human_sample",
            "clarifications": {
                "collection_date": "2023-06-15",
            },
        })

    # With the clarification provided, it should now be submitted
    assert result["status"] == "submitted"

    # The accession should be whatever the mock returned
    assert result["accession"] == "SAMEA999001"

    # The message should mention BioSamples
    assert "BioSamples" in result["message"]


@pytest.mark.asyncio
async def test_complete_description_submits_directly():
    """Verify that a fully described sample submits without needing clarification.

    A description that includes organism, tissue, date, and disease should
    pass the default checklist validation and go straight to submission.
    """

    # Mock the submit call — we don't want to hit the real API in tests
    with patch("src.tools.smart_submit_tool.run_submit_tool", new_callable=AsyncMock) as mock_submit:
        # Fake a successful submission response
        mock_submit.return_value = {"accession": "SAMEA999002", "status": "submitted"}

        # This description has all the default required fields
        result = await run_smart_submit_tool({
            "description": "Human blood sample from Germany 2023 with diabetes",
            "checklist": "default",
        })

    # Should go directly to submitted status
    assert result["status"] == "submitted"

    # Accession should match our mock return value
    assert result["accession"] == "SAMEA999002"
