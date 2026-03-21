# Natural Language Search page — parse plain English queries into BioSamples filters
# Demonstrates that users don't need to know the BioSamples query syntax

import sys
import os

# Add the project root so the import resolves correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pandas as pd
import streamlit as st

# Import the natural search helper from the API client
from ui.utils.api_client import natural_search

# Page configuration
st.set_page_config(
    page_title="Natural Language Search — BioSamples MCP",
    page_icon="🧬",
    layout="wide",
)

# Page heading
st.title("Natural Language Search")

# One-line description
st.write(
    "Describe what samples you are looking for in plain English. "
    "The server parses your query into structured BioSamples filters automatically."
)

# Divider below the header
st.divider()

# Initialize the query key in session state on the very first load
# This must happen before any widget reads from it
if "nl_query" not in st.session_state:
    # Start blank so the input renders empty on first visit
    st.session_state["nl_query"] = ""

# --- Example query buttons ---
# Each button writes to st.session_state["nl_query"] then reruns,
# so the text input below always picks up the new value via value=

# Label for the example section
st.caption("Example queries:")

# Three columns for the three example buttons
ex1, ex2, ex3 = st.columns(3)

with ex1:
    # Oncology — simple two-word query that reliably returns results
    if st.button("human lung cancer"):
        # Set the shared key — the text input reads this on rerun
        st.session_state["nl_query"] = "human lung cancer"
        # Rerun so the input re-renders with the new value
        st.rerun()

with ex2:
    # Kidney biopsy with disease and location — all human samples
    if st.button("human kidney biopsy Berlin 2022"):
        # Set the shared key — the text input reads this on rerun
        st.session_state["nl_query"] = "human kidney biopsy Berlin 2022"
        st.rerun()

with ex3:
    # COVID-19 blood samples — tests disease and tissue extraction
    if st.button("human blood COVID-19 Germany"):
        # Set the shared key — the text input reads this on rerun
        st.session_state["nl_query"] = "human blood COVID-19 Germany"
        st.rerun()

# --- Query input ---

# Text input has no key= so Streamlit never takes ownership of its value
# value= is always respected on every render, reading fresh from session state
query = st.text_input(
    "What samples are you looking for?",
    # Always read from session state — this is what the buttons write to
    value=st.session_state["nl_query"],
    placeholder="e.g. Human blood samples from Europe after 2020 related to diabetes",
)

# Primary search button
search_clicked = st.button("Search", type="primary")

# --- Results ---

# Only run the search when the button is clicked and the query is non-empty
if search_clicked and query.strip():
    # Save whatever the user typed so it survives reruns
    st.session_state["nl_query"] = query.strip()

    # Spinner while the server processes the request
    with st.spinner("Understanding your query..."):
        # Call the natural language search endpoint
        response = natural_search(query.strip())

    # Check for errors from the API client
    if "error" in response:
        # Show the error in a red box
        st.error(response["error"])

    else:
        # Unwrap the result dict from the server response envelope
        tool_result = response.get("result", response)

        # --- Interpreted query panel ---
        # Show the user what the server understood from their query text
        interpreted = tool_result.get("query_interpreted_as", {})

        # Only show the interpretation panel if something was extracted
        if interpreted:
            # Neutral info panel heading
            st.subheader("Query interpreted as")

            # Convert the interpreted dict to a single-row DataFrame for display
            interp_df = pd.DataFrame([interpreted])

            # Rename columns to title case for nicer display
            interp_df.columns = [c.replace("_", " ").title() for c in interp_df.columns]

            # Display the interpretation as a table
            st.dataframe(
                interp_df,
                use_container_width=True,
                hide_index=True,
            )

        # Divider between the interpretation and the results
        st.divider()

        # --- Results table ---

        # Get the results list from the tool output
        results = tool_result.get("results", [])

        # Count header showing how many records came back
        results_count = tool_result.get("results_count", len(results))
        st.success(f"Found {results_count} samples")

        if results:
            # Build a display-friendly list of row dicts
            rows = []
            for sample in results:
                rows.append({
                    "Accession": sample.get("accession", ""),
                    "Name": sample.get("name", ""),
                    "Organism": sample.get("organism", ""),
                    "Tissue": sample.get("tissue", ""),
                    "Disease": sample.get("disease", ""),
                    "Location": sample.get("geographic_location", ""),
                    "Collection date": sample.get("collection_date", ""),
                    "BioSamples link": f"https://www.ebi.ac.uk/biosamples/samples/{sample.get('accession', '')}",
                })

            # Create a pandas DataFrame from the rows
            df = pd.DataFrame(rows)

            # Display the results table with a clickable link column
            st.dataframe(
                df,
                column_config={
                    # Render the link column as a clickable URL
                    "BioSamples link": st.column_config.LinkColumn(
                        "BioSamples link",
                        display_text="View",
                    )
                },
                # Fill the full page width
                use_container_width=True,
                # Hide the default 0-based integer row index
                hide_index=True,
            )

        else:
            # No results — explain this gracefully
            st.info(
                "No samples matched the interpreted filters. "
                "Try rephrasing your query with different organism, tissue, or disease terms."
            )

elif search_clicked and not query.strip():
    # User clicked Search with an empty input
    st.warning("Please enter a search query.")
