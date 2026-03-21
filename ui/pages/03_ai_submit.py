# AI-Assisted Submission page — the showcase feature of this project
# Shows the full workflow: plain text input → metadata extraction → clarification → submission
# This page is the most important one for demos and job interviews

import sys
import os

# Add the project root to the path so the import resolves
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st

# Import the smart submit helper
from ui.utils.api_client import smart_submit

# Page configuration
st.set_page_config(
    page_title="AI-Assisted Submission — BioSamples MCP",
    page_icon="🧬",
    layout="wide",
)

# Page heading
st.title("AI-Assisted Sample Submission")

# Explanatory subtitle
st.write(
    "Describe your biological sample in plain English. "
    "The server extracts metadata automatically, validates it against BioSamples checklists, "
    "and asks for any missing information before submitting."
)

# Divider below the header
st.divider()

# Initialize the description key in session state on the very first load
# This must happen before any widget reads from it
if "description" not in st.session_state:
    # Start with an empty string so the text area renders blank
    st.session_state["description"] = ""

# --- Example description buttons ---
# Each button overwrites st.session_state["description"] then reruns,
# so the text area below always picks up the new value via value=

# Label above the example buttons
st.caption("Example descriptions:")

# Three columns for the three example buttons
ex1, ex2, ex3 = st.columns(3)

with ex1:
    # Human liver sample — covers the most fields
    if st.button("Human liver cirrhosis, London 2023"):
        # Set the shared session state key — the text area reads this on rerun
        st.session_state["description"] = (
            "Human liver biopsy collected in London in 2023 from a patient with cirrhosis."
        )
        # Clear any previous clarification state when a new example is loaded
        st.session_state.pop("clarification_result", None)
        st.session_state.pop("clarification_answers", None)
        # Rerun so the text area re-renders with the new value
        st.rerun()

with ex2:
    # Human kidney sample — demonstrates tissue and disease extraction for non-liver organs
    if st.button("Human kidney diabetes, Berlin 2022"):
        # Set the shared session state key — the text area reads this on rerun
        st.session_state["description"] = (
            "Human kidney biopsy from a diabetes patient collected in Berlin 2022."
        )
        st.session_state.pop("clarification_result", None)
        st.session_state.pop("clarification_answers", None)
        # Rerun so the text area re-renders with the new value
        st.rerun()

with ex3:
    # COVID-19 sample — tests disease and year extraction
    if st.button("Human blood COVID-19 Germany"):
        # Set the shared session state key — the text area reads this on rerun
        st.session_state["description"] = (
            "Human blood sample from a 45-year-old male patient in Germany with COVID-19."
        )
        st.session_state.pop("clarification_result", None)
        st.session_state.pop("clarification_answers", None)
        # Rerun so the text area re-renders with the new value
        st.rerun()

# --- Description input ---

# Text area has no key= so Streamlit never takes ownership of its value
# value= is always respected on every render, reading fresh from session state
description = st.text_area(
    "Describe your biological sample",
    # Always read from session state — this is what the buttons write to
    value=st.session_state["description"],
    placeholder=(
        "e.g. Human liver biopsy collected in London in 2023 "
        "from a patient with cirrhosis"
    ),
    # Taller input box so longer descriptions are comfortable to read
    height=120,
)

# Checklist selector — radio buttons for the two supported checklists
checklist_label = st.radio(
    "Validation checklist",
    options=["Default (minimum fields)", "Human sample (stricter validation)"],
    horizontal=True,
)

# Map the human-readable label back to the API parameter value
checklist = "default" if "Default" in checklist_label else "human_sample"

# Primary action button
analyze_clicked = st.button("Analyze Description", type="primary")

# --- Workflow Step A: Initial analysis ---

if analyze_clicked and description.strip():
    # Save whatever the user typed so it survives the rerun after analysis
    st.session_state["description"] = description.strip()

    # Clear any previous clarification state so the page starts fresh
    st.session_state.pop("clarification_result", None)
    st.session_state.pop("clarification_answers", None)

    # Show a spinner while the server processes the description
    with st.spinner("Analyzing description..."):
        # Call the smart submit endpoint with no clarifications yet
        result = smart_submit(description.strip(), checklist=checklist)

    # Check for server errors before trying to render the result
    if "error" in result:
        # Show the error message so the user can diagnose the issue
        st.error(result["error"])

    else:
        # Unwrap the tool result from the server response envelope
        tool_result = result.get("result", result)

        # Store the result in session state so the clarification form can read it
        st.session_state["clarification_result"] = tool_result
        st.session_state["clarification_checklist"] = checklist

        # Trigger a rerun so the clarification form renders below
        st.rerun()

elif analyze_clicked and not description.strip():
    # Remind the user to enter a description before clicking
    st.warning("Please enter a sample description.")

# --- Workflow Step B: Show clarification form or success ---

# Only render this section if we have a result stored from a previous analysis
if "clarification_result" in st.session_state:
    # Retrieve the stored analysis result
    tool_result = st.session_state["clarification_result"]

    # Divider to visually separate analysis output from the input section
    st.divider()

    # --- Case 1: Submission succeeded immediately (all fields were present) ---
    if tool_result.get("status") == "submitted":
        # Green success box with the assigned accession
        st.success("Sample submitted successfully")

        # Show the accession number prominently
        accession = tool_result.get("accession", "")
        st.markdown(f"**Accession: {accession}**")

        # Direct link to the new sample on EMBL-EBI
        st.link_button(
            "View on EMBL-EBI BioSamples",
            f"https://www.ebi.ac.uk/biosamples/samples/{accession}",
        )

        # Show the submitted metadata so the user can verify what was sent
        submitted_meta = tool_result.get("submitted_metadata", {})
        if submitted_meta:
            # Subheading for the metadata table
            st.subheader("Submitted metadata")

            # Convert the metadata dict to a two-column display
            for key, value in submitted_meta.items():
                # Skip the additional_metadata nested dict — it would look messy inline
                if key != "additional_metadata":
                    st.write(f"**{key}:** {value}")

        # Reset button so the user can start a new submission
        if st.button("Submit another sample"):
            # Clear all stored state so the page resets to its initial state
            st.session_state.pop("clarification_result", None)
            st.session_state["description"] = ""
            st.rerun()

    # --- Case 2: Missing fields — show extracted metadata and clarification questions ---
    elif tool_result.get("status") == "needs_clarification":
        # Show what the server extracted automatically
        extracted = tool_result.get("extracted_so_far", {})

        # Only show the extraction panel if we actually got some fields
        if extracted:
            # Green panel heading — auto-extraction worked for these fields
            st.success("Metadata extracted from description")

            # Two columns to display extracted fields side by side
            left, right = st.columns(2)

            # List of fields to show in the left column
            left_fields = ["organism", "tissue", "collection_date"]
            # List of fields to show in the right column
            right_fields = ["disease", "geographic_location", "age", "sex"]

            with left:
                for field in left_fields:
                    if field in extracted:
                        # Display each extracted field as a bold label + value
                        st.write(f"**{field.replace('_', ' ').title()}:** {extracted[field]}")

            with right:
                for field in right_fields:
                    if field in extracted:
                        st.write(f"**{field.replace('_', ' ').title()}:** {extracted[field]}")

        # Divider between extracted and missing sections
        st.divider()

        # Retrieve the clarification questions from the result
        questions = tool_result.get("questions", [])
        missing_fields = tool_result.get("missing_required", [])

        # Show a neutral info box listing the missing fields
        st.info(f"Additional information required: {', '.join(missing_fields)}")

        # Initialize the answers dict in session state if not already there
        if "clarification_answers" not in st.session_state:
            # Start with an empty dict so the text inputs render blank
            st.session_state["clarification_answers"] = {}

        # Render one text input for each clarification question
        for i, (field, question) in enumerate(zip(missing_fields, questions)):
            # Text input labeled with the question text — key ties it to the field name
            answer = st.text_input(
                question,
                # Restore previous answer if the user already typed one
                value=st.session_state["clarification_answers"].get(field, ""),
                key=f"clarification_{field}",
            )
            # Save the answer immediately to session state
            if answer:
                st.session_state["clarification_answers"][field] = answer

        # Button to submit the collected answers back to the server
        submit_with_answers = st.button("Submit with answers", type="primary")

        if submit_with_answers:
            # Read all the current answer values from session state
            answers = {
                field: st.session_state.get(f"clarification_{field}", "")
                for field in missing_fields
            }

            # Filter out any fields the user left blank
            answers = {k: v for k, v in answers.items() if v.strip()}

            # Only proceed if at least one answer was provided
            if answers:
                # Call the server again with the description and the user's answers
                with st.spinner("Submitting sample..."):
                    # Retrieve the original description from session state
                    orig_description = st.session_state.get("description", "")
                    orig_checklist = st.session_state.get("clarification_checklist", "default")

                    # Call smart_submit with the clarification answers included
                    result2 = smart_submit(
                        orig_description,
                        checklist=orig_checklist,
                        clarifications=answers,
                    )

                if "error" in result2:
                    # Show the error so the user knows what went wrong
                    st.error(result2["error"])
                else:
                    # Unwrap the new result and store it — this triggers a rerun
                    new_tool_result = result2.get("result", result2)
                    st.session_state["clarification_result"] = new_tool_result
                    st.rerun()

            else:
                # User clicked submit without answering any questions
                st.warning("Please answer at least one question before submitting.")
