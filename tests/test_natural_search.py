# Tests for the natural_search_biosamples tool
# Covers NLP filter extraction and the live search integration

import pytest
from unittest.mock import AsyncMock, patch

from src.nlp_parser import parse_sample_description
from src.tools.natural_search_tool import run_natural_search_tool


def test_diabetes_blood_query_extracts_correct_filters():
    """Verify that a diabetes blood query extracts the right structured filters.

    We test the NLP parser directly here since the tool delegates extraction to it.
    The parser should recognize human, blood, and diabetes from a natural query.
    """

    # A query someone might type into a search box
    result = parse_sample_description("human blood diabetes samples from Germany")

    # Organism should be Homo sapiens
    assert result["extracted"]["organism"] == "Homo sapiens"

    # Tissue should be blood
    assert result["extracted"]["tissue"] == "blood"

    # Disease should be diabetes
    assert result["extracted"]["disease"] == "diabetes"

    # Location should be Germany
    assert result["extracted"]["geographic_location"] == "Germany"


@pytest.mark.asyncio
async def test_natural_search_returns_structured_results():
    """Verify that the natural search tool returns the expected response structure.

    Mocks the BioSamples API so we can test the response format without
    needing live data. Checks that all expected fields are present.
    """

    # Build a fake API response that looks like a real BioSamples sample
    fake_samples = [
        {
            "accession": "SAMEA112654119",
            "name": "Human blood sample",
            "characteristics": {
                "organism": [{"text": "Homo sapiens"}],
                "disease or disorder": [{"text": "diabetes"}],
                "tissue": [{"text": "blood"}],
                "collection date": [{"text": "2021-03-15"}],
                "geographic location (country and/or sea)": [{"text": "Germany"}],
            },
        }
    ]

    # Mock search_samples in the natural_search_tool module
    with patch("src.tools.natural_search_tool.search_samples", new_callable=AsyncMock) as mock_search:
        # Return our fake sample list when the search is called
        mock_search.return_value = fake_samples

        # Run the tool with a natural language query
        result = await run_natural_search_tool({
            "query": "human blood diabetes samples Germany"
        })

    # Tool name should be set correctly in the response
    assert result["tool"] == "natural_search_biosamples"

    # Should have the interpreted filters for transparency
    assert "query_interpreted_as" in result

    # Results count should match the length of our fake list
    assert result["results_count"] == 1

    # Each result should have an accession field
    assert result["results"][0]["accession"] == "SAMEA112654119"

    # Disease should be normalized from the characteristics
    assert result["results"][0]["disease"] == "diabetes"
