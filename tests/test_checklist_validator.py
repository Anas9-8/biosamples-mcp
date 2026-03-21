# Tests for the checklist validator — all synchronous, no network needed
# Verifies required/recommended field checking and clarification question generation

from src.checklist_validator import validate_sample


def test_complete_metadata_passes_default_checklist():
    """Verify that metadata with all required fields passes the default checklist."""

    # Build a metadata dict that has at least organism and taxon_id (default required fields)
    metadata = {
        "organism": "Homo sapiens",
        "taxon_id": 9606,
        "tissue": "liver",
        "disease": "cirrhosis",
        "collection_date": "2023-01-01",
        "geographic_location": "United Kingdom",
    }

    # Run against the default checklist which only requires organism and taxon_id
    result = validate_sample(metadata, "default")

    # All required fields are present so valid should be True
    assert result["valid"] is True

    # No required fields should be flagged as missing
    assert result["missing_required"] == []

    # The sample should be ready to submit
    assert result["ready_to_submit"] is True


def test_missing_organism_fails_default_checklist():
    """Verify that metadata missing organism fails the default checklist."""

    # A metadata dict without the required organism field
    metadata = {
        "tissue": "blood",
        "disease": "healthy",
    }

    # Default checklist requires organism and taxon_id — both are missing here
    result = validate_sample(metadata, "default")

    # Should not be valid since organism is required
    assert result["valid"] is False

    # organism and taxon_id should both be in the missing list
    assert "organism" in result["missing_required"]

    # Should not be ready to submit
    assert result["ready_to_submit"] is False

    # Should have clarification questions for each missing required field
    assert len(result["clarification_questions"]) > 0


def test_human_checklist_requires_collection_date():
    """Verify that the human_sample checklist flags missing collection_date."""

    # Metadata that has organism but no collection date
    metadata = {
        "organism": "Homo sapiens",
        "taxon_id": 9606,
        "tissue": "liver",
    }

    # Human sample checklist additionally requires tissue and collection_date
    result = validate_sample(metadata, "human_sample")

    # collection_date is required by human_sample checklist and missing here
    assert "collection_date" in result["missing_required"]

    # The clarification questions should ask about collection date
    assert any("collected" in q.lower() for q in result["clarification_questions"])

    # Should not be ready to submit without collection_date
    assert result["ready_to_submit"] is False


def test_unknown_checklist_falls_back_to_default():
    """Verify that an unknown checklist name falls back to default gracefully."""

    # A metadata dict with only the default required fields
    metadata = {"organism": "Mus musculus", "taxon_id": 10090}

    # Use a checklist name that doesn't exist — should fall back to default
    result = validate_sample(metadata, "nonexistent_checklist")

    # Default only requires organism and taxon_id — both are present
    assert result["valid"] is True
