# Pydantic models for BioSamples data — used for validation and type safety
# BioSample covers the fetch/read path; SubmitSampleRequest covers the write path

from typing import Optional
from pydantic import BaseModel


class BioSample(BaseModel):
    """Represents a sample fetched from BioSamples.

    Maps the key fields from a BioSamples API response into a typed Python
    object. The characteristics field holds the raw attribute dict since its
    structure varies by sample type.
    """

    # Primary identifier assigned by BioSamples (e.g. SAMEA112654119)
    accession: str

    # Human-readable label for the sample
    name: str

    # Scientific name of the organism (e.g. Homo sapiens, SARS-CoV-2)
    organism: str

    # NCBI Taxonomy ID — optional because not all samples include it
    taxon_id: Optional[int] = None

    # ISO date the sample was collected — often missing in older records
    collection_date: Optional[str] = None

    # Country or region where the sample was collected
    geographic_location: Optional[str] = None

    # Tissue type — e.g. blood, lung, liver
    tissue: Optional[str] = None

    # Disease association if any — e.g. COVID-19, lung cancer
    disease: Optional[str] = None

    # Raw characteristics dict from the API — structure varies per sample
    characteristics: dict = {}


class SubmitSampleRequest(BaseModel):
    """Input model for submitting a new sample to BioSamples.

    All core biological fields are required at submission time. The
    additional_metadata dict lets callers include extra attributes without
    needing a new model field for each one.
    """

    # Name for the sample — should be descriptive and unique within your domain
    name: str

    # Scientific organism name — must match NCBI taxonomy for indexing
    organism: str

    # NCBI Taxonomy ID — required at submission, unlike in fetch responses
    taxon_id: int

    # Tissue type the sample came from
    tissue: str

    # Disease context or "healthy" if no disease association
    disease: str

    # Collection date in ISO 8601 format: YYYY-MM-DD
    collection_date: str

    # Country or region using GAZ ontology terms where possible
    geographic_location: str

    # Any additional key-value attributes to include with the sample
    additional_metadata: Optional[dict] = {}
