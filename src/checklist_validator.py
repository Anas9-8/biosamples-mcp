# Validate extracted sample metadata against BioSamples checklist JSON files
# Checklists live in the checklists/ directory next to the project root
# Returns missing fields and ready-made clarification questions for the user

import json
import os

# Locate the checklists directory relative to this source file
# src/ is one level below the project root, so we go up two levels from here
_SRC_DIR = os.path.dirname(__file__)
_CHECKLIST_DIR = os.path.join(_SRC_DIR, "..", "checklists")

# Human-readable clarification questions for each field the user might be missing
CLARIFICATION_QUESTIONS = {
    # These are phrased as a researcher would ask a colleague
    "organism": "What organism is this sample from? (e.g. Homo sapiens, Mus musculus)",
    "taxon_id": "What is the NCBI taxon ID? (e.g. 9606 for human, 10090 for mouse)",
    "tissue": "What tissue type is this sample from? (e.g. blood, liver, lung)",
    "collection_date": "When was this sample collected? (YYYY-MM-DD format, e.g. 2023-06-15)",
    "disease": "Is there a disease association? If healthy, just say 'healthy'",
    "geographic_location": "In which country was this sample collected? (e.g. Germany, United Kingdom)",
    "age": "What is the donor age in years? (e.g. 45)",
    "sex": "What is the donor sex? (male / female / unknown)",
}


def _load_checklist(checklist_name: str) -> dict:
    """Load a checklist JSON file by its short name (without .json extension)."""

    # Build the full path to the checklist file
    checklist_path = os.path.join(_CHECKLIST_DIR, f"{checklist_name}.json")

    # If the file doesn't exist, fall back to the default checklist
    if not os.path.exists(checklist_path):
        # Use default instead of crashing — safer for unknown checklist names
        checklist_path = os.path.join(_CHECKLIST_DIR, "default.json")

    # Open and parse the JSON file
    with open(checklist_path) as f:
        # Return the parsed dict directly
        return json.load(f)


def validate_sample(metadata: dict, checklist: str = "default") -> dict:
    """Check if a metadata dict satisfies the required and recommended checklist fields.

    Returns a dict telling the caller what's missing and what questions to ask
    the user to fill in the gaps. 'ready_to_submit' is True only if all required
    fields are present in the metadata.
    """

    # Load the checklist rules from disk
    rules = _load_checklist(checklist)

    # Find which required fields are absent from the metadata
    missing_required = [f for f in rules["required"] if not metadata.get(f)]

    # Find which recommended fields are absent — not blocking but worth flagging
    missing_recommended = [f for f in rules["recommended"] if not metadata.get(f)]

    # Build a list of clarification questions for every missing required field
    clarification_questions = [
        # Look up the human-friendly question text for each missing field
        CLARIFICATION_QUESTIONS.get(field, f"Please provide: {field}")
        for field in missing_required
    ]

    # The sample is ready to submit only when no required fields are missing
    ready_to_submit = len(missing_required) == 0

    # valid means there are no required fields missing at all
    valid = ready_to_submit

    # Return the full validation result so the caller can decide what to do
    return {
        "valid": valid,
        "checklist": checklist,
        "missing_required": missing_required,
        "missing_recommended": missing_recommended,
        "clarification_questions": clarification_questions,
        "ready_to_submit": ready_to_submit,
    }
