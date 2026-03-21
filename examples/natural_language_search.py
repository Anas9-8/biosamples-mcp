# Demo: Natural language search using the natural_search_biosamples tool
# Run this with: python3 examples/natural_language_search.py
# Shows how plain English queries become structured BioSamples searches

import asyncio
import sys
import os

# Add the project root to sys.path so we can import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools.natural_search_tool import run_natural_search_tool


async def demo_natural_search(query: str):
    """Run a single natural language search and print the results as a table."""

    # Print the query so the demo output is self-explanatory
    print(f"\nQuery: '{query}'")
    print("-" * 60)

    # Call the tool with the raw natural language query
    result = await run_natural_search_tool({"query": query})

    # Show what the NLP parser understood from the query text
    print(f"Interpreted as: {result['query_interpreted_as']}")

    # Show how many results came back from BioSamples
    print(f"Results found: {result['results_count']}")

    # Print each result as a simple table row
    if result["results"]:
        # Print a header row for the table
        print(f"\n{'Accession':<18} {'Organism':<20} {'Tissue':<12} {'Disease':<15} {'Country':<15}")
        print("-" * 80)

        for sample in result["results"]:
            # Format each field with fixed width so columns align
            accession = sample.get("accession", "")[:17]
            organism = sample.get("organism", "")[:19]
            tissue = sample.get("tissue", "")[:11]
            disease = sample.get("disease", "")[:14]
            country = sample.get("geographic_location", "")[:14]

            # Print the row with consistent column widths
            print(f"{accession:<18} {organism:<20} {tissue:<12} {disease:<15} {country:<15}")

    else:
        # No results — tell the user so they don't wonder if the tool broke
        print("No results found for this query.")


async def run_all_demos():
    """Run three different example queries to demonstrate range of use cases."""

    # Print the demo header
    print("=" * 60)
    print("NATURAL LANGUAGE SEARCH DEMO")
    print("=" * 60)

    # Demo 1: Search for COVID-19 lung samples — pandemic-era research data
    await demo_natural_search("human lung cancer samples from 2022")

    # Demo 2: Search for diabetes-related blood samples from a specific country
    await demo_natural_search("blood samples Germany diabetes")

    # Demo 3: Mouse liver samples — common in pre-clinical research
    await demo_natural_search("mouse liver hepatitis samples")

    # Print a closing separator
    print("\n" + "=" * 60)
    print("Demo complete. These queries hit the real BioSamples API.")
    print("=" * 60)


# Entry point — runs all three demo queries when called directly
if __name__ == "__main__":
    asyncio.run(run_all_demos())
