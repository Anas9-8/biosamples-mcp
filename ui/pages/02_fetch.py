# Fetch page — retrieve and display full metadata for a specific BioSamples accession
# Useful for looking up detailed sample info after finding an accession in a search

import sys
import os

# Add the project root so the import path resolves correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st

# Import the fetch helper from the API client
from ui.utils.api_client import fetch_sample

# Page configuration
st.set_page_config(
    page_title="Fetch Sample — BioSamples MCP",
    page_icon="🧬",
    layout="wide",
)

# Page heading
st.title("Fetch Sample Details")

# One-sentence description of this page
st.write("Enter a BioSamples accession to retrieve its full metadata from EMBL-EBI.")

# Divider below the header
st.divider()

# --- Pre-load buttons ---
# These allow quick demo loading without typing an accession

# Label above the shortcut buttons
st.caption("Quick load:")

# Two columns for the two pre-set accession buttons
btn1, btn2 = st.columns(2)

with btn1:
    # Our own submitted sample — most relevant for demos
    if st.button("SAMEA122005222  (submitted by us)"):
        # Store the accession in session state so the input reads it
        st.session_state["fetch_prefill"] = "SAMEA122005222"
        st.rerun()

with btn2:
    # A real well-known human sample from EBI
    if st.button("SAMEA112654119  (human sample)"):
        st.session_state["fetch_prefill"] = "SAMEA112654119"
        st.rerun()

# --- Accession input ---

# Text input — reads pre-fill from session state if a button was clicked
accession = st.text_input(
    "BioSamples accession",
    value=st.session_state.get("fetch_prefill", ""),
    placeholder="e.g. SAMEA122005222",
)

# Primary fetch button
fetch_clicked = st.button("Fetch Sample", type="primary")

# --- Result display ---

# Only fetch if the button was clicked and the accession field is not empty
if fetch_clicked and accession.strip():
    # Spinner to indicate the outgoing API call
    with st.spinner("Fetching from EMBL-EBI..."):
        # Call the REST endpoint through the helper
        response = fetch_sample(accession.strip())

    # Check for errors returned by the helper
    if "error" in response:
        # Show the error in red
        st.error(response["error"])

    else:
        # Unwrap the sample dict from the server response envelope
        sample = response.get("result", response)

        # Pull the characteristics dict — most metadata lives here
        chars = sample.get("characteristics", {})

        # Helper to safely extract the first text value from a characteristic list
        def get_char(key: str) -> str:
            """Return the first text value for a characteristic key, or empty string."""
            entries = chars.get(key, [])
            return entries[0].get("text", "") if entries else ""

        # Display the sample name as the main heading
        st.subheader(sample.get("name", accession))

        # Divider before the metadata columns
        st.divider()

        # Two columns — left for identifiers, right for biological context
        left, right = st.columns(2)

        with left:
            # Primary accession identifier
            st.write(f"**Accession:** {sample.get('accession', '')}")
            # Scientific organism name
            st.write(f"**Organism:** {get_char('organism')}")
            # Release/submission date from the top-level field
            st.write(f"**Release date:** {sample.get('release', '')[:10]}")
            # Submission date from BioSamples metadata
            st.write(f"**Submitted:** {sample.get('submitted', '')[:10] if sample.get('submitted') else 'not available'}")

        with right:
            # Tissue type
            st.write(f"**Tissue:** {get_char('tissue')}")
            # Disease association
            st.write(f"**Disease:** {get_char('disease') or get_char('disease or disorder')}")
            # Geographic location using the full attribute name BioSamples uses
            st.write(f"**Location:** {get_char('geographic location (country and/or sea)')}")
            # Sample collection date
            st.write(f"**Collection date:** {get_char('collection date')}")

        # Divider before the raw characteristics expander
        st.divider()

        # Collapsible section for the raw characteristics — useful for developers
        with st.expander("Raw characteristics"):
            # Iterate over all characteristic keys and display them in a simple list
            for key, values in chars.items():
                # Extract just the text values from the nested list structure
                texts = [v.get("text", "") for v in values if v.get("text")]
                # Display as "key: value" pair
                st.write(f"**{key}:** {', '.join(texts)}")

        # Link button to the official EMBL-EBI entry for this sample
        st.link_button(
            "View on EMBL-EBI BioSamples",
            f"https://www.ebi.ac.uk/biosamples/samples/{sample.get('accession', accession)}",
        )

elif fetch_clicked and not accession.strip():
    # Remind the user to enter an accession before clicking
    st.warning("Please enter an accession number.")
