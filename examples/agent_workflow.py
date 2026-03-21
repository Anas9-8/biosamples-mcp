# Example: how an AI agent would use the BioSamples MCP server
# This script simulates the kind of workflow a research assistant might run:
# 1. Search for lung cancer samples
# 2. Fetch full metadata for the top 3 results
# 3. Print a clean formatted summary
#
# Concrete examples used in this script:
#   SAMEA112654119 — human tissue sample with detailed metadata
#   SAMEA7997453   — COVID-19 related sample showing disease tracking use case

import asyncio
from src.biosamples_client import search_samples, get_sample


async def run_agent_workflow():
    """Simulate an agent searching BioSamples and fetching detailed metadata.

    This is the pattern an LLM agent would follow: broad search first,
    then targeted fetch for the samples that look most relevant.
    """

    # Step 1: search for lung cancer samples from the 2020-2023 window
    print("Searching BioSamples for human lung cancer samples (2020-2023)...")
    search_query = "human lung cancer samples 2020 2023"

    # Run the search — we ask for 5 results to have options
    results = await search_samples(query=search_query, page_size=5)

    # Let the user know how many we found
    print(f"Found {len(results)} matching samples\n")

    # Step 2: take the top 3 results and fetch their full metadata
    top_results = results[:3]

    # Keep track of the fetched samples for the summary
    fetched_samples = []

    for i, sample_summary in enumerate(top_results, start=1):
        # Get the accession from the summary — this is what we use to fetch
        accession = sample_summary.get("accession", "unknown")

        # Let the user see progress
        print(f"Fetching full metadata for sample {i}: {accession}")

        # Fetch the complete metadata for this sample
        full_sample = await get_sample(accession)

        # Store the full metadata for the summary section
        fetched_samples.append(full_sample)

    # Step 3: print a clean formatted summary for each fetched sample
    print("\n" + "=" * 60)
    print("SAMPLE SUMMARY REPORT")
    print("=" * 60 + "\n")

    for sample in fetched_samples:
        # Pull the accession and name from the top-level fields
        accession = sample.get("accession", "N/A")
        name = sample.get("name", "N/A")

        # Characteristics are nested dicts with lists of text objects
        characteristics = sample.get("characteristics", {})

        # Extract organism — it's a list with one text entry
        organism_list = characteristics.get("organism", [{}])
        organism = organism_list[0].get("text", "N/A") if organism_list else "N/A"

        # Extract tissue if available
        tissue_list = characteristics.get("tissue", [{}])
        tissue = tissue_list[0].get("text", "N/A") if tissue_list else "N/A"

        # Extract disease if available
        disease_list = characteristics.get("disease or disorder", [{}])
        disease = disease_list[0].get("text", "N/A") if disease_list else "N/A"

        # Extract collection date if available
        date_list = characteristics.get("collection date", [{}])
        collection_date = date_list[0].get("text", "N/A") if date_list else "N/A"

        # Print the summary block for this sample
        print(f"Accession:       {accession}")
        print(f"Name:            {name}")
        print(f"Organism:        {organism}")
        print(f"Tissue:          {tissue}")
        print(f"Disease:         {disease}")
        print(f"Collection Date: {collection_date}")
        print("-" * 60 + "\n")


# Run the workflow when this script is executed directly
if __name__ == "__main__":
    # Use asyncio.run to execute the async workflow
    asyncio.run(run_agent_workflow())
