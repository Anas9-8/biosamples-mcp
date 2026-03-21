# Search page — lets users search the BioSamples database by keyword
# Accessible from the Streamlit sidebar as "Search Samples"

import sys
import os

# Add the project root so we can import from ui/utils/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pandas as pd
import streamlit as st

# Import the REST client helper
from ui.utils.api_client import search_samples

# Page-level configuration
st.set_page_config(
    page_title="Search Samples — BioSamples MCP",
    page_icon="🧬",
    layout="wide",
)

# Page heading — short and descriptive
st.title("Search Biological Samples")

# One-line description of what this page does
st.write("Search the EMBL-EBI BioSamples database. Results link directly to the BioSamples website.")

# Horizontal divider between header and controls
st.divider()

# Initialize the search query key in session state on the very first load
# This must happen before any widget reads from it
if "search_query" not in st.session_state:
    # Start blank so the input renders empty on first visit
    st.session_state["search_query"] = ""

# --- Example query buttons ---
# Each button writes to st.session_state["search_query"] then reruns,
# so the text input below always picks up the new value via value=

# Section label above the example buttons
st.caption("Example searches:")

# Three columns for the three example buttons
ex1, ex2, ex3 = st.columns(3)

with ex1:
    # "human" is a broad term that reliably returns many results from BioSamples
    if st.button("human"):
        # Set the shared key — the text input reads this on rerun
        st.session_state["search_query"] = "human"
        # Rerun so the input re-renders with the new value
        st.rerun()

with ex2:
    # "blood" matches the tissue attribute directly — consistently returns results
    if st.button("blood"):
        # Set the shared key — the text input reads this on rerun
        st.session_state["search_query"] = "blood"
        st.rerun()

with ex3:
    # "liver" is a common tissue type with broad coverage in BioSamples
    if st.button("liver"):
        # Set the shared key — the text input reads this on rerun
        st.session_state["search_query"] = "liver"
        st.rerun()

# --- Search input ---

# Text input has no key= so Streamlit never takes ownership of its value
# value= is always respected on every render, reading fresh from session state
query = st.text_input(
    "Search query",
    # Always read from session state — this is what the buttons write to
    value=st.session_state["search_query"],
    placeholder="e.g. human, blood, liver, lung cancer",
)

# Search button — user clicks this to run the query
search_clicked = st.button("Search Samples", type="primary")

# --- Results ---

# Only run a search if the button was clicked and there is a query string
if search_clicked and query.strip():
    # Save whatever the user typed so it survives reruns
    st.session_state["search_query"] = query.strip()

    # Show a spinner so the user knows a network call is in progress
    with st.spinner("Searching EMBL-EBI BioSamples..."):
        # Call the REST API through the helper
        response = search_samples(query.strip())

    # Check if the server returned an error
    if "error" in response:
        # Display the error message in a red box
        st.error(response["error"])

    else:
        # Unwrap the result list from the server response envelope
        results = response.get("result", [])

        # Show how many records came back
        st.success(f"Found {len(results)} samples")

        if results:
            # Build a display-ready DataFrame from the result list
            rows = []
            for sample in results:
                # Each row gets the four key fields agents care about
                rows.append({
                    "Accession": sample.get("accession", ""),
                    "Name": sample.get("name", ""),
                    "Organism": sample.get("organism", ""),
                    "Disease": sample.get("disease", ""),
                })

            # Create a pandas DataFrame for clean tabular display
            df = pd.DataFrame(rows)

            # Add a clickable URL column so users can open any sample on EMBL-EBI
            df["BioSamples link"] = df["Accession"].apply(
                lambda acc: f"https://www.ebi.ac.uk/biosamples/samples/{acc}"
            )

            # Display the table — column_config lets us render the link as a clickable URL
            st.dataframe(
                df,
                column_config={
                    # Render the BioSamples link column as a clickable hyperlink
                    "BioSamples link": st.column_config.LinkColumn(
                        "BioSamples link",
                        display_text="View",
                    )
                },
                # Stretch the table to fill the full page width
                use_container_width=True,
                # Hide the default integer row index
                hide_index=True,
            )

        else:
            # No results is not an error — just tell the user
            st.info("No samples found for this query. Try a different search term.")

elif search_clicked and not query.strip():
    # User clicked Search without typing anything — gentle nudge
    st.warning("Please enter a search query before clicking Search.")
