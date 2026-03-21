# Extract BioSamples metadata fields from a plain English description
# No external AI APIs needed — pure regex and keyword matching keeps it fast and offline
# Example: "Human liver biopsy from London 2023" → organism, tissue, location, date

import re

# Map common plain-English organism names to their scientific names and NCBI taxon IDs
ORGANISM_MAP = {
    # Human variants people commonly write in free text
    "human": ("Homo sapiens", 9606),
    "humans": ("Homo sapiens", 9606),
    "patient": ("Homo sapiens", 9606),
    "woman": ("Homo sapiens", 9606),
    "man": ("Homo sapiens", 9606),
    "person": ("Homo sapiens", 9606),
    # Mouse — very common in lab research samples
    "mouse": ("Mus musculus", 10090),
    "mice": ("Mus musculus", 10090),
    "murine": ("Mus musculus", 10090),
    # Rat — another common lab animal
    "rat": ("Rattus norvegicus", 10116),
    "rats": ("Rattus norvegicus", 10116),
}

# Tissues we can recognize from plain English text — checked as whole words
TISSUE_KEYWORDS = [
    # Ordered from multi-word to single-word so longer matches win
    "bone marrow",
    "lymph node",
    "blood",
    "liver",
    "kidney",
    "lung",
    "brain",
    "heart",
    "skin",
    "muscle",
    "spleen",
    "pancreas",
]

# Diseases and conditions we can recognize — checked case-insensitively
DISEASE_KEYWORDS = [
    # Multi-word diseases first so they aren't split
    "COVID-19",
    "Alzheimer's",
    "Parkinson's",
    "bone marrow cancer",
    "cancer",
    "diabetes",
    "cirrhosis",
    "leukemia",
    "tuberculosis",
    "malaria",
    "hepatitis",
]

# Map city/country keywords to the full country name BioSamples expects
COUNTRY_MAP = {
    # UK has many aliases
    "london": "United Kingdom",
    "uk": "United Kingdom",
    "britain": "United Kingdom",
    "england": "United Kingdom",
    "united kingdom": "United Kingdom",
    # European countries
    "germany": "Germany",
    "berlin": "Germany",
    "france": "France",
    "paris": "France",
    "italy": "Italy",
    "rome": "Italy",
    "spain": "Spain",
    "madrid": "Spain",
    "netherlands": "Netherlands",
    "sweden": "Sweden",
    # Asia
    "china": "China",
    "japan": "Japan",
    "india": "India",
    # Americas
    "united states": "United States",
    "usa": "United States",
    "us": "United States",
    "america": "United States",
    "brazil": "Brazil",
}

# These fields must all be present for a submission — used to build the "missing" list
REQUIRED_FIELDS = ["organism", "taxon_id", "tissue", "collection_date"]


def parse_sample_description(text: str) -> dict:
    """Extract BioSamples metadata fields from a plain text description.

    Returns a dict with three keys: 'extracted' (fields we found),
    'missing' (required fields we couldn't find), and 'confidence'
    ('full' if nothing required is missing, otherwise 'partial').
    """

    # Work with lowercase text so matching isn't case-sensitive
    lower = text.lower()

    # Start with an empty dict — we'll fill it as we find matches
    extracted = {}

    # --- Organism detection ---
    # Scan for each organism keyword and take the first match we find
    for keyword, (sci_name, taxon) in ORGANISM_MAP.items():
        # Use word boundary so "human" doesn't match inside "inhumane"
        if re.search(rf"\b{re.escape(keyword)}\b", lower):
            # Store the scientific name and taxon ID together
            extracted["organism"] = sci_name
            extracted["taxon_id"] = taxon
            # Stop at the first match — no need to keep scanning
            break

    # --- Tissue detection ---
    # Check multi-word tissues first so "bone marrow" beats "marrow"
    for tissue in TISSUE_KEYWORDS:
        # Simple substring check is fine here — tissues are specific words
        if tissue in lower:
            # Store just the tissue name as a plain string
            extracted["tissue"] = tissue
            # Only keep the first tissue we find
            break

    # --- Disease detection ---
    # COVID-19 needs special handling because of the hyphen
    for disease in DISEASE_KEYWORDS:
        # Case-insensitive check — "covid-19" and "COVID-19" both match
        if disease.lower() in lower:
            # Store the disease with its canonical casing
            extracted["disease"] = disease
            # Take the first disease match and stop
            break

    # --- Collection date from year mention ---
    # Look for a 4-digit year in the 1900s or 2000s
    year_match = re.search(r"\b((?:19|20)\d{2})\b", text)
    if year_match:
        # Expand the year to a full ISO date — day and month default to 01
        extracted["collection_date"] = f"{year_match.group(1)}-01-01"

    # --- Geographic location ---
    # Check every known city/country name against the lowercased text
    for keyword, country in COUNTRY_MAP.items():
        if keyword in lower:
            # Store the normalized country name
            extracted["geographic_location"] = country
            # Stop at first match — one location per sample
            break

    # --- Age extraction ---
    # Look for patterns like "45-year-old" or "45 year old"
    age_match = re.search(r"\b(\d+)[- ]year", lower)
    if age_match:
        # Store the age as a plain string, not an integer
        extracted["age"] = age_match.group(1)

    # --- Sex detection ---
    # Check for the word "male" but not inside "female"
    if re.search(r"\bfemale\b", lower):
        # Female must be checked first since "female" contains "male"
        extracted["sex"] = "female"
    elif re.search(r"\bmale\b", lower):
        # Now safe to check for plain "male"
        extracted["sex"] = "male"

    # --- Build the missing required fields list ---
    # Anything in REQUIRED_FIELDS that isn't in extracted goes in missing
    missing = [field for field in REQUIRED_FIELDS if field not in extracted]

    # Confidence is "full" only when all required fields were found
    confidence = "full" if not missing else "partial"

    # Return the standard three-key response dict
    return {
        "extracted": extracted,
        "missing": missing,
        "confidence": confidence,
    }
