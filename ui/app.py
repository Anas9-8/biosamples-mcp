# Main entry point for the BioSamples MCP Streamlit web interface
# Run with: streamlit run ui/app.py
# This page is the home/dashboard — individual tools are in ui/pages/

import sys
import os

# Add the project root to sys.path so ui/ can import from src/ if needed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st

# Import the API client helper that calls localhost:8000
from utils.api_client import check_server_health, fetch_sample

# Configure the Streamlit page — this must be the first Streamlit call
st.set_page_config(
    # Tab title shown in the browser
    page_title="BioSamples MCP Tools",
    # Small icon shown in the browser tab
    page_icon="🧬",
    # Wide layout gives more room for tables and results
    layout="wide",
    # Sidebar starts expanded so users see the server status immediately
    initial_sidebar_state="expanded",
)

# --- Sidebar ---

# Application title in the sidebar
st.sidebar.title("BioSamples MCP")

# Brief subtitle describing what this tool does
st.sidebar.caption("AI-Powered Biological Sample Management")

# Visual separator between branding and controls
st.sidebar.divider()

# Check if the REST server is responding before rendering status
server_online = check_server_health()

# Show green text if the server is up, red if it is down
if server_online:
    # Green markdown text — Streamlit supports limited HTML-like coloring via markdown
    st.sidebar.markdown(
        "<span style='color:#2ecc71; font-weight:600'>Server: Online</span>",
        unsafe_allow_html=True,
    )
else:
    # Red text to make the offline state immediately visible
    st.sidebar.markdown(
        "<span style='color:#e74c3c; font-weight:600'>Server: Offline</span>",
        unsafe_allow_html=True,
    )
    # Give the user the exact command to bring the server up
    st.sidebar.caption("Start with: uvicorn src.server:app --reload")

# Divider between server status and the token input
st.sidebar.divider()

# AAP token input — stored in session_state so all pages can read it
# type="password" hides the token value in the browser
st.sidebar.text_input(
    "AAP Token (required for submission)",
    # Read back from session state if it was already entered on another page
    value=st.session_state.get("aap_token", ""),
    type="password",
    # Store the token in session state so all pages share the same value
    key="aap_token",
    # Short help text so users know where to get the token
    help="Get a token from https://aai.ebi.ac.uk",
)

# Another divider before the info section at the bottom of the sidebar
st.sidebar.divider()

# Informational note — reassures users this connects to the real API
st.sidebar.info("Connected to EMBL-EBI BioSamples API")

# GitHub repository link at the bottom of the sidebar
st.sidebar.markdown(
    "[View on GitHub](https://github.com/Anas9-8/biosamples-mcp)",
    unsafe_allow_html=False,
)

# --- Main Page ---

# Large page heading
st.title("BioSamples MCP Tools")

# Descriptive subtitle below the main heading
st.write("AI-powered interface for the EMBL-EBI BioSamples database.")

# Horizontal rule to separate the header from the metrics row
st.divider()

# Four metric cards in a single row — gives a dashboard feel
col1, col2, col3, col4 = st.columns(4)

# First card: total number of tools available
with col1:
    st.metric(label="MCP Tools Available", value="5")

# Second card: the underlying data source
with col2:
    st.metric(label="Data Source", value="EMBL-EBI")

# Third card: submission type
with col3:
    st.metric(label="Submission", value="Real-time")

# Fourth card: workflow type
with col4:
    st.metric(label="Workflow", value="AI-Assisted")

# Divider between the metrics and the capabilities section
st.divider()

# Section heading for the capability overview
st.subheader("Available Tools")

# Four equal columns, one for each major capability
cap1, cap2, cap3, cap4 = st.columns(4)

# Search tool description card
with cap1:
    # Thin bordered container to visually separate each capability
    with st.container(border=True):
        # Tool name as a small heading
        st.markdown("**Search Samples**")
        # One-line description of what this tool does
        st.write("Query the BioSamples database by keyword, organism, disease, or tissue.")

# Fetch tool description card
with cap2:
    with st.container(border=True):
        st.markdown("**Fetch Sample Details**")
        st.write("Retrieve complete metadata for any BioSamples accession.")

# AI Submit tool description card
with cap3:
    with st.container(border=True):
        st.markdown("**AI-Assisted Submission**")
        st.write("Describe your sample in plain English. The server extracts and validates metadata automatically.")

# Natural language search description card
with cap4:
    with st.container(border=True):
        st.markdown("**Natural Language Search**")
        st.write("Search using plain English — no need to know the BioSamples query syntax.")

# Divider before the quick demo section
st.divider()

# Section heading for the live demo widget
st.subheader("Quick Demo")

# Short instruction so users know what to expect when they click
st.write("Fetch a real BioSamples record to verify the server is connected.")

# Button to load the sample we submitted during development
if st.button("Load sample SAMEA122005222"):
    # Show a spinner while the API call is in progress
    with st.spinner("Fetching from EMBL-EBI..."):
        # Call the fetch endpoint for our known accession
        result = fetch_sample("SAMEA122005222")

    # Check if the call returned an error
    if "error" in result:
        # Show the error in red so the user can diagnose the problem
        st.error(result["error"])
    else:
        # Unwrap the result — the server wraps tool output in a 'result' key
        sample = result.get("result", result)

        # Show the sample name as a subheader
        st.subheader(sample.get("name", "Sample"))

        # Two columns for the key metadata fields
        left, right = st.columns(2)

        with left:
            # Accession identifier
            st.write(f"**Accession:** {sample.get('accession', '')}")
            # Organism name from characteristics
            chars = sample.get("characteristics", {})
            # Pull organism text from the nested characteristics list
            organism = chars.get("organism", [{}])[0].get("text", "") if chars.get("organism") else ""
            st.write(f"**Organism:** {organism}")

        with right:
            # Tissue type if available
            tissue = chars.get("tissue", [{}])[0].get("text", "") if chars.get("tissue") else ""
            st.write(f"**Tissue:** {tissue}")
            # Collection date if available
            cdate = chars.get("collection date", [{}])[0].get("text", "") if chars.get("collection date") else ""
            st.write(f"**Collection date:** {cdate}")

        # Direct link to the EMBL-EBI website entry for this sample
        st.markdown(
            "[View on EMBL-EBI BioSamples](https://www.ebi.ac.uk/biosamples/samples/SAMEA122005222)"
        )
