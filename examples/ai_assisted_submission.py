# Demo: AI-assisted submission workflow using the smart_submit_biosample tool
# Run this with: python3 examples/ai_assisted_submission.py
# Shows the full conversation flow: description → clarification → submission

import asyncio
import sys
import os

# Add the project root to the path so we can import src modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.tools.smart_submit_tool import run_smart_submit_tool


async def demo_ai_assisted_submission():
    """Show the complete AI-assisted submission workflow step by step."""

    # The user's initial plain-text description — no structured fields needed
    user_description = "Human blood sample from Germany 2023 with COVID-19"

    # Print what the user typed so the demo is easy to follow
    print("=" * 60)
    print("AI-ASSISTED BIOSAMPLES SUBMISSION DEMO")
    print("=" * 60)
    print(f"\nUser input: '{user_description}'")
    print("\nStep 1: Parsing description and checking required fields...")

    # Call the smart submit tool with just the description first
    result = await run_smart_submit_tool({
        "description": user_description,
        # Use default checklist for this demo — only organism and taxon_id required
        "checklist": "default",
    })

    # Print what the NLP parser extracted automatically
    print(f"\nExtracted so far: {result.get('extracted_so_far', {})}")

    # Check if the tool needs more info from the user
    if result["status"] == "needs_clarification":
        # Show the clarification questions to the user
        print("\nClarification questions:")
        for i, question in enumerate(result["questions"], 1):
            # Number each question so the user knows how many there are
            print(f"  {i}. {question}")

        # Simulate the user answering the clarification questions
        print("\nStep 2: User provides clarification answers...")

        # Hard-coded answers for the demo — in production these come from the user
        clarifications = {"sex": "male"}
        print(f"User answers: {clarifications}")

        # Call again with the same description plus the clarification answers
        result = await run_smart_submit_tool({
            "description": user_description,
            "checklist": "default",
            "clarifications": clarifications,
        })

    # Check if the submission went through or if we need even more info
    if result["status"] == "submitted":
        # Print the success result with the assigned BioSamples accession
        print(f"\n✓ {result['message']}")
        print(f"  Accession: {result['accession']}")
        print(f"  Submitted metadata: {result.get('submitted_metadata', {})}")

    elif result["status"] == "needs_clarification":
        # Still missing fields even after clarification — tell the user
        print("\nStill missing required fields:")
        for question in result["questions"]:
            # Print each remaining question so the user knows what to provide
            print(f"  - {question}")

    else:
        # Something unexpected happened — print the full result for debugging
        print(f"\nUnexpected result: {result}")

    # Print a separator for readability
    print("\n" + "=" * 60)


async def demo_with_all_fields():
    """Show a submission that goes straight through without clarification."""

    # A fully described sample — all required fields extractable from the text
    full_description = "Human liver biopsy collected in United Kingdom in 2023 from a patient with cirrhosis"

    print("\nDemo 2: Fully described sample (no clarification needed)")
    print(f"Input: '{full_description}'")

    # Call without specifying checklist — defaults to the minimum required fields
    result = await run_smart_submit_tool({
        "description": full_description,
        "checklist": "default",
    })

    # Show the result — should go straight to submitted or needs_clarification
    print(f"Result status: {result['status']}")
    if result["status"] == "submitted":
        # Print the accession from the (mocked or real) submission
        print(f"Accession: {result['accession']}")
    else:
        # Show what's still missing so the user knows what to add to the description
        print(f"Still missing: {result.get('missing_required', [])}")
        print(f"Questions: {result.get('questions', [])}")


# Run both demos when this script is executed directly
if __name__ == "__main__":
    asyncio.run(demo_ai_assisted_submission())
    asyncio.run(demo_with_all_fields())
