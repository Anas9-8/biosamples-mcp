# Tests for the NLP parser — all synchronous, no network, no mocks needed
# These verify that plain English sentences produce the right extracted fields

from src.nlp_parser import parse_sample_description


def test_human_liver_london_2023():
    """Verify a typical human sample description extracts the right fields.

    The sentence has organism (human), tissue (liver), location (London → UK),
    disease (cirrhosis), and year (2023) — all should be extracted correctly.
    """

    # A realistic sentence a researcher might type when submitting a sample
    result = parse_sample_description(
        "Human liver biopsy collected in London in 2023 from a patient with cirrhosis."
    )

    # Organism should be normalized to the scientific name
    assert result["extracted"]["organism"] == "Homo sapiens"

    # Taxon ID for Homo sapiens is 9606
    assert result["extracted"]["taxon_id"] == 9606

    # Liver should be extracted as the tissue type
    assert result["extracted"]["tissue"] == "liver"

    # London should map to United Kingdom in the country map
    assert result["extracted"]["geographic_location"] == "United Kingdom"

    # Cirrhosis is in the disease keyword list
    assert result["extracted"]["disease"] == "cirrhosis"

    # The year 2023 should expand to 2023-01-01
    assert result["extracted"]["collection_date"] == "2023-01-01"


def test_mouse_kidney_extracts_correct_organism():
    """Verify that 'mouse' maps to Mus musculus and the right taxon ID."""

    # A minimal mouse sample description
    result = parse_sample_description("Mouse kidney sample from a diabetes study, collected in Berlin.")

    # Mouse should map to the scientific name Mus musculus
    assert result["extracted"]["organism"] == "Mus musculus"

    # NCBI taxon ID for mouse is 10090
    assert result["extracted"]["taxon_id"] == 10090

    # Kidney is in the tissue keyword list
    assert result["extracted"]["tissue"] == "kidney"

    # Berlin should map to Germany
    assert result["extracted"]["geographic_location"] == "Germany"

    # Diabetes is a recognized disease keyword
    assert result["extracted"]["disease"] == "diabetes"


def test_covid_lung_sample():
    """Verify COVID-19 and lung are extracted from a typical pandemic-era description."""

    # COVID-19 samples are common in BioSamples — this tests the hyphenated disease name
    result = parse_sample_description("COVID-19 lung sample collected in 2021 from Italy.")

    # Lung should be detected as the tissue
    assert result["extracted"]["tissue"] == "lung"

    # COVID-19 must match including the hyphen
    assert result["extracted"]["disease"] == "COVID-19"

    # Italy should be in the country map
    assert result["extracted"]["geographic_location"] == "Italy"


def test_empty_string_returns_empty_extracted():
    """Verify that an empty input doesn't crash and returns empty extracted dict."""

    # Edge case: empty string should never raise an exception
    result = parse_sample_description("")

    # Should return a dict with the expected three keys
    assert "extracted" in result

    # No fields should be extracted from an empty string
    assert result["extracted"] == {}

    # All required fields should be flagged as missing
    assert "organism" in result["missing"]

    # Confidence should be partial since we're missing required fields
    assert result["confidence"] == "partial"


def test_age_and_sex_extraction():
    """Verify that age and sex are extracted from a clinical description."""

    # A description mentioning patient demographics
    result = parse_sample_description("Blood sample from a 45-year-old male patient in Germany with COVID-19.")

    # Age should be extracted as a string
    assert result["extracted"]["age"] == "45"

    # Sex should be extracted as "male"
    assert result["extracted"]["sex"] == "male"

    # Blood should be the tissue
    assert result["extracted"]["tissue"] == "blood"
