# Architecture page — three HTML/CSS diagrams replacing graphviz
# Uses 00_ prefix so it appears first in the Streamlit sidebar

import sys
import os

# Add the project root so imports from ui/ resolve correctly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import streamlit as st

# Import the HTML component renderer
import streamlit.components.v1 as components

# Page configuration — wide layout for the diagrams
st.set_page_config(
    page_title="System Architecture — BioSamples MCP",
    page_icon="",
    layout="wide",
)

# Page heading
st.title("System Architecture")

# Subtitle describing what this page covers
st.write(
    "How the BioSamples MCP server connects AI agents "
    "to the EMBL-EBI BioSamples database."
)

# Horizontal divider below the header
st.divider()

# ================================================================
# DIAGRAM 1 — System Overview (HTML/CSS)
# ================================================================

# Section heading for diagram 1
st.subheader("Diagram 1 — System Overview")

# Explanation paragraph for diagram 1
st.write(
    "The server exposes five MCP tools through two transports: "
    "a FastAPI REST server on port 8000 for HTTP clients "
    "and a FastMCP stdio server for Claude Desktop. "
    "Two AI-powered tools use an embedded intelligence layer "
    "before reaching the EMBL-EBI BioSamples API."
)

# Full HTML string for diagram 1 — system overview flowchart
# Every layer is a colored row, arrows go straight down, no crossing
DIAGRAM_1_HTML = """
<div style="font-family:Arial,sans-serif;max-width:920px;margin:0 auto;background:#fafafa;padding:28px 18px 18px 18px;border-radius:14px;box-shadow:0 2px 16px rgba(0,0,0,0.07);">

  <!-- CLIENT LAYER -->
  <div style="background:#e8f4fd;border-radius:10px;padding:14px 10px 12px 10px;margin-bottom:0;">
    <div style="text-align:center;font-size:11px;font-weight:700;color:#1f77b4;letter-spacing:1.5px;margin-bottom:10px;">CLIENT LAYER</div>
    <div style="display:flex;justify-content:center;gap:18px;">
      <!-- Streamlit UI box -->
      <div style="background:#1f77b4;color:#fff;border-radius:8px;padding:12px 18px;text-align:center;min-width:170px;box-shadow:0 2px 8px rgba(31,119,180,0.25);">
        <div style="font-weight:700;font-size:13px;">Streamlit UI</div>
        <div style="font-size:11px;opacity:0.85;margin-top:2px;">port 8501</div>
      </div>
      <!-- LLM Agent box -->
      <div style="background:#1f77b4;color:#fff;border-radius:8px;padding:12px 18px;text-align:center;min-width:170px;box-shadow:0 2px 8px rgba(31,119,180,0.25);">
        <div style="font-weight:700;font-size:13px;">LLM Agent</div>
        <div style="font-size:11px;opacity:0.85;margin-top:2px;">Claude Desktop</div>
      </div>
      <!-- REST Client box -->
      <div style="background:#1f77b4;color:#fff;border-radius:8px;padding:12px 18px;text-align:center;min-width:170px;box-shadow:0 2px 8px rgba(31,119,180,0.25);">
        <div style="font-weight:700;font-size:13px;">REST Client</div>
        <div style="font-size:11px;opacity:0.85;margin-top:2px;">curl / HTTP</div>
      </div>
    </div>
  </div>

  <!-- ARROWS: clients to servers -->
  <div style="display:flex;justify-content:center;gap:18px;margin:0;">
    <!-- Left arrow: Streamlit -> FastAPI (blue) -->
    <div style="display:flex;flex-direction:column;align-items:center;min-width:170px;">
      <div style="width:3px;height:32px;background:#1f77b4;"></div>
      <div style="font-size:10px;color:#1f77b4;font-weight:600;margin:-2px 0 -2px 0;">HTTP POST</div>
      <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #1f77b4;"></div>
    </div>
    <!-- Middle arrow: Agent -> MCP (purple) -->
    <div style="display:flex;flex-direction:column;align-items:center;min-width:170px;">
      <div style="width:3px;height:32px;background:#9467bd;"></div>
      <div style="font-size:10px;color:#9467bd;font-weight:600;margin:-2px 0 -2px 0;">stdio</div>
      <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #9467bd;"></div>
    </div>
    <!-- Right arrow: REST Client -> FastAPI (blue) -->
    <div style="display:flex;flex-direction:column;align-items:center;min-width:170px;">
      <div style="width:3px;height:32px;background:#1f77b4;"></div>
      <div style="font-size:10px;color:#1f77b4;font-weight:600;margin:-2px 0 -2px 0;">HTTP POST</div>
      <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #1f77b4;"></div>
    </div>
  </div>

  <!-- SERVER LAYER -->
  <div style="background:#e8f8e8;border-radius:10px;padding:14px 10px 12px 10px;margin-bottom:0;">
    <div style="text-align:center;font-size:11px;font-weight:700;color:#2ca02c;letter-spacing:1.5px;margin-bottom:10px;">SERVER LAYER</div>
    <div style="display:flex;justify-content:center;gap:28px;">
      <!-- FastAPI REST Server box -->
      <div style="background:#2ca02c;color:#fff;border-radius:8px;padding:12px 22px;text-align:center;min-width:220px;box-shadow:0 2px 8px rgba(44,160,44,0.22);">
        <div style="font-weight:700;font-size:13px;">FastAPI REST Server</div>
        <div style="font-size:11px;opacity:0.85;margin-top:2px;">port 8000 &middot; src/server.py</div>
      </div>
      <!-- FastMCP stdio Server box -->
      <div style="background:#2ca02c;color:#fff;border-radius:8px;padding:12px 22px;text-align:center;min-width:220px;box-shadow:0 2px 8px rgba(44,160,44,0.22);">
        <div style="font-weight:700;font-size:13px;">FastMCP stdio Server</div>
        <div style="font-size:11px;opacity:0.85;margin-top:2px;">Claude Desktop &middot; src/mcp_server.py</div>
      </div>
    </div>
  </div>

  <!-- ARROWS: servers to tools -->
  <div style="display:flex;justify-content:center;gap:28px;margin:0;">
    <!-- Green arrows from FastAPI -->
    <div style="display:flex;flex-direction:column;align-items:center;min-width:220px;">
      <div style="width:3px;height:28px;background:#2ca02c;"></div>
      <div style="font-size:10px;color:#2ca02c;font-weight:600;margin:-2px 0 -2px 0;">dispatches to all 5 tools</div>
      <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #2ca02c;"></div>
    </div>
    <!-- Purple arrows from MCP -->
    <div style="display:flex;flex-direction:column;align-items:center;min-width:220px;">
      <div style="width:3px;height:28px;background:#9467bd;"></div>
      <div style="font-size:10px;color:#9467bd;font-weight:600;margin:-2px 0 -2px 0;">dispatches to all 5 tools</div>
      <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #9467bd;"></div>
    </div>
  </div>

  <!-- TOOLS LAYER -->
  <div style="background:#fff3e0;border-radius:10px;padding:14px 10px 12px 10px;margin-bottom:0;">
    <div style="text-align:center;font-size:11px;font-weight:700;color:#e65100;letter-spacing:1.5px;margin-bottom:10px;">TOOL LAYER</div>
    <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;">
      <!-- search_biosamples box — standard orange -->
      <div style="background:#ff7f0e;color:#fff;border-radius:8px;padding:10px 12px;text-align:center;min-width:130px;box-shadow:0 2px 8px rgba(255,127,14,0.22);">
        <div style="font-weight:700;font-size:12px;">search</div>
        <div style="font-size:10px;opacity:0.85;">biosamples</div>
      </div>
      <!-- fetch_biosample box — standard orange -->
      <div style="background:#ff7f0e;color:#fff;border-radius:8px;padding:10px 12px;text-align:center;min-width:130px;box-shadow:0 2px 8px rgba(255,127,14,0.22);">
        <div style="font-weight:700;font-size:12px;">fetch</div>
        <div style="font-size:10px;opacity:0.85;">biosample</div>
      </div>
      <!-- submit_biosample box — standard orange -->
      <div style="background:#ff7f0e;color:#fff;border-radius:8px;padding:10px 12px;text-align:center;min-width:130px;box-shadow:0 2px 8px rgba(255,127,14,0.22);">
        <div style="font-weight:700;font-size:12px;">submit</div>
        <div style="font-size:10px;opacity:0.85;">biosample</div>
      </div>
      <!-- smart_submit_biosample box — AI red -->
      <div style="background:#d62728;color:#fff;border-radius:8px;padding:10px 12px;text-align:center;min-width:130px;box-shadow:0 2px 8px rgba(214,39,40,0.22);">
        <div style="font-weight:700;font-size:12px;">smart_submit</div>
        <div style="font-size:10px;opacity:0.85;">biosample</div>
      </div>
      <!-- natural_search_biosamples box — AI red -->
      <div style="background:#d62728;color:#fff;border-radius:8px;padding:10px 12px;text-align:center;min-width:130px;box-shadow:0 2px 8px rgba(214,39,40,0.22);">
        <div style="font-weight:700;font-size:12px;">natural_search</div>
        <div style="font-size:10px;opacity:0.85;">biosamples</div>
      </div>
    </div>
  </div>

  <!-- ARROWS: AI tools to intelligence layer -->
  <div style="display:flex;justify-content:center;gap:60px;margin:0;">
    <div style="display:flex;flex-direction:column;align-items:center;">
      <div style="width:3px;height:28px;background:#d62728;"></div>
      <div style="font-size:10px;color:#d62728;font-weight:600;margin:-2px 0 -2px 0;">parse text</div>
      <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #d62728;"></div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:center;">
      <div style="width:3px;height:28px;background:#d62728;"></div>
      <div style="font-size:10px;color:#d62728;font-weight:600;margin:-2px 0 -2px 0;">validate fields</div>
      <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #d62728;"></div>
    </div>
  </div>

  <!-- INTELLIGENCE LAYER -->
  <div style="background:#f3e8ff;border-radius:10px;padding:14px 10px 12px 10px;margin-bottom:0;">
    <div style="text-align:center;font-size:11px;font-weight:700;color:#7b2d8e;letter-spacing:1.5px;margin-bottom:10px;">INTELLIGENCE LAYER</div>
    <div style="display:flex;justify-content:center;gap:28px;">
      <!-- nlp_parser.py box -->
      <div style="background:#9467bd;color:#fff;border-radius:8px;padding:12px 22px;text-align:center;min-width:220px;box-shadow:0 2px 8px rgba(148,103,189,0.22);">
        <div style="font-weight:700;font-size:13px;">nlp_parser.py</div>
        <div style="font-size:11px;opacity:0.85;margin-top:2px;">text to metadata extraction</div>
      </div>
      <!-- checklist_validator.py box -->
      <div style="background:#9467bd;color:#fff;border-radius:8px;padding:12px 22px;text-align:center;min-width:220px;box-shadow:0 2px 8px rgba(148,103,189,0.22);">
        <div style="font-weight:700;font-size:13px;">checklist_validator.py</div>
        <div style="font-size:11px;opacity:0.85;margin-top:2px;">field validation + questions</div>
      </div>
    </div>
  </div>

  <!-- ARROWS: intelligence to API -->
  <div style="display:flex;justify-content:center;margin:0;">
    <div style="display:flex;flex-direction:column;align-items:center;">
      <div style="width:3px;height:28px;background:#7f7f7f;"></div>
      <div style="font-size:10px;color:#7f7f7f;font-weight:600;margin:-2px 0 -2px 0;">validated metadata</div>
      <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #7f7f7f;"></div>
    </div>
  </div>

  <!-- API LAYER -->
  <div style="background:#f0f0f0;border-radius:10px;padding:14px 10px 12px 10px;margin-bottom:14px;">
    <div style="text-align:center;font-size:11px;font-weight:700;color:#555;letter-spacing:1.5px;margin-bottom:10px;">EXTERNAL API</div>
    <div style="display:flex;justify-content:center;">
      <!-- BioSamples API box -->
      <div style="background:#555;color:#fff;border-radius:8px;padding:14px 36px;text-align:center;min-width:480px;box-shadow:0 2px 8px rgba(0,0,0,0.15);">
        <div style="font-weight:700;font-size:14px;">EMBL-EBI BioSamples API</div>
        <div style="font-size:11px;opacity:0.85;margin-top:3px;">https://www.ebi.ac.uk/biosamples</div>
        <div style="font-size:10px;opacity:0.7;margin-top:4px;">GET /samples?text=  &middot;  GET /samples/{id}  &middot;  POST /samples</div>
      </div>
    </div>
  </div>

  <!-- COLOR LEGEND -->
  <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;padding:8px 0 0 0;border-top:1px solid #e0e0e0;">
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#1f77b4;"></div><span style="font-size:11px;color:#444;">Client Layer</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#2ca02c;"></div><span style="font-size:11px;color:#444;">Server Layer</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#ff7f0e;"></div><span style="font-size:11px;color:#444;">Standard Tools</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#d62728;"></div><span style="font-size:11px;color:#444;">AI-Powered Tools</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#9467bd;"></div><span style="font-size:11px;color:#444;">Intelligence Layer</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#555;"></div><span style="font-size:11px;color:#444;">External API</span></div>
  </div>

</div>
"""

# Render diagram 1 as an HTML component — height accommodates all 5 layers
components.html(DIAGRAM_1_HTML, height=900, scrolling=False)

# Divider before diagram 2
st.divider()

# ================================================================
# DIAGRAM 2 — AI-Assisted Submission Workflow (HTML/CSS)
# ================================================================

# Section heading for diagram 2
st.subheader("Diagram 2 — AI-Assisted Submission Workflow")

# Explanation paragraph for diagram 2
st.write(
    "The smart_submit_biosample tool accepts a plain English "
    "description and runs it through two pipeline stages. "
    "If required fields are missing, clarification questions "
    "are returned instead of submitting an incomplete record. "
    "Both paths converge at the final submission step."
)

# Full HTML string for diagram 2 — vertical workflow with branching paths
DIAGRAM_2_HTML = """
<div style="font-family:Arial,sans-serif;max-width:820px;margin:0 auto;background:#fafafa;padding:28px 18px 18px 18px;border-radius:14px;box-shadow:0 2px 16px rgba(0,0,0,0.07);">

  <!-- STEP 1: User Input -->
  <div style="display:flex;justify-content:center;">
    <div style="background:#1f77b4;color:#fff;border-radius:8px;padding:14px 28px;text-align:center;min-width:420px;box-shadow:0 2px 8px rgba(31,119,180,0.25);">
      <div style="font-weight:700;font-size:14px;">1. User Input</div>
      <div style="font-size:12px;opacity:0.9;margin-top:4px;">Plain English description</div>
      <div style="font-size:11px;opacity:0.75;margin-top:3px;font-style:italic;">"Human liver biopsy London 2023 with cirrhosis"</div>
    </div>
  </div>

  <!-- Arrow: input to NLP (blue) -->
  <div style="display:flex;flex-direction:column;align-items:center;">
    <div style="width:3px;height:24px;background:#1f77b4;"></div>
    <div style="font-size:10px;color:#1f77b4;font-weight:600;">plain text</div>
    <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #1f77b4;"></div>
  </div>

  <!-- STEP 2: NLP Parser -->
  <div style="display:flex;justify-content:center;">
    <div style="background:#9467bd;color:#fff;border-radius:8px;padding:14px 28px;text-align:center;min-width:420px;box-shadow:0 2px 8px rgba(148,103,189,0.22);">
      <div style="font-weight:700;font-size:14px;">2. nlp_parser.py</div>
      <div style="font-size:12px;opacity:0.9;margin-top:4px;">Extracts structured fields:</div>
      <div style="display:flex;justify-content:center;gap:8px;margin-top:6px;flex-wrap:wrap;">
        <span style="background:rgba(255,255,255,0.2);padding:2px 8px;border-radius:4px;font-size:10px;">organism</span>
        <span style="background:rgba(255,255,255,0.2);padding:2px 8px;border-radius:4px;font-size:10px;">tissue</span>
        <span style="background:rgba(255,255,255,0.2);padding:2px 8px;border-radius:4px;font-size:10px;">disease</span>
        <span style="background:rgba(255,255,255,0.2);padding:2px 8px;border-radius:4px;font-size:10px;">location</span>
        <span style="background:rgba(255,255,255,0.2);padding:2px 8px;border-radius:4px;font-size:10px;">date</span>
      </div>
    </div>
  </div>

  <!-- Arrow: NLP to validator (purple) -->
  <div style="display:flex;flex-direction:column;align-items:center;">
    <div style="width:3px;height:24px;background:#9467bd;"></div>
    <div style="font-size:10px;color:#9467bd;font-weight:600;">extracted fields</div>
    <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #9467bd;"></div>
  </div>

  <!-- STEP 3: Checklist Validator -->
  <div style="display:flex;justify-content:center;">
    <div style="background:#9467bd;color:#fff;border-radius:8px;padding:14px 28px;text-align:center;min-width:420px;box-shadow:0 2px 8px rgba(148,103,189,0.22);">
      <div style="font-weight:700;font-size:14px;">3. checklist_validator.py</div>
      <div style="font-size:12px;opacity:0.9;margin-top:4px;">Checks fields against selected checklist</div>
      <div style="font-size:10px;opacity:0.75;margin-top:4px;">default: organism required &nbsp;|&nbsp; human_sample: organism + tissue + date</div>
    </div>
  </div>

  <!-- Arrow: validator to decision split -->
  <div style="display:flex;flex-direction:column;align-items:center;">
    <div style="width:3px;height:20px;background:#9467bd;"></div>
  </div>

  <!-- DECISION SPLIT: two columns -->
  <div style="display:flex;justify-content:center;gap:30px;">

    <!-- LEFT PATH: fields missing (red) -->
    <div style="display:flex;flex-direction:column;align-items:center;flex:1;max-width:340px;">
      <!-- Decision label: No -->
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
        <div style="width:22px;height:22px;background:#d62728;color:#fff;border-radius:50%;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;">?</div>
        <span style="font-size:11px;color:#d62728;font-weight:700;">Fields missing</span>
      </div>
      <!-- Arrow down red -->
      <div style="width:3px;height:14px;background:#d62728;"></div>
      <div style="width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-top:8px solid #d62728;"></div>
      <!-- Step 4a: Clarification -->
      <div style="background:#d62728;color:#fff;border-radius:8px;padding:12px 16px;text-align:center;width:100%;margin-top:2px;box-shadow:0 2px 8px rgba(214,39,40,0.22);">
        <div style="font-weight:700;font-size:13px;">4a. Clarification Questions</div>
        <div style="font-size:11px;opacity:0.9;margin-top:3px;">e.g. "When was this collected?"</div>
        <div style="font-size:11px;opacity:0.9;">e.g. "What is the donor sex?"</div>
      </div>
      <!-- Arrow down blue (user answers) -->
      <div style="display:flex;flex-direction:column;align-items:center;">
        <div style="width:3px;height:14px;background:#1f77b4;"></div>
        <div style="font-size:10px;color:#1f77b4;font-weight:600;">user answers</div>
        <div style="width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-top:8px solid #1f77b4;"></div>
      </div>
      <!-- Step 5: Merge -->
      <div style="background:#9467bd;color:#fff;border-radius:8px;padding:12px 16px;text-align:center;width:100%;margin-top:2px;box-shadow:0 2px 8px rgba(148,103,189,0.22);">
        <div style="font-weight:700;font-size:13px;">5. Merge + Revalidate</div>
        <div style="font-size:11px;opacity:0.9;margin-top:2px;">combine answers with extracted fields</div>
      </div>
      <!-- Arrow down to merge point -->
      <div style="width:3px;height:20px;background:#9467bd;"></div>
      <div style="width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-top:8px solid #9467bd;"></div>
    </div>

    <!-- RIGHT PATH: all fields present (green) -->
    <div style="display:flex;flex-direction:column;align-items:center;flex:1;max-width:340px;">
      <!-- Decision label: Yes -->
      <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
        <div style="width:22px;height:22px;background:#2ca02c;color:#fff;border-radius:50%;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;">&#10003;</div>
        <span style="font-size:11px;color:#2ca02c;font-weight:700;">All fields present</span>
      </div>
      <!-- Long green arrow down to submit step -->
      <div style="width:3px;height:250px;background:#2ca02c;"></div>
      <div style="width:0;height:0;border-left:6px solid transparent;border-right:6px solid transparent;border-top:8px solid #2ca02c;"></div>
    </div>

  </div>

  <!-- STEP 6: Submit — both paths merge here -->
  <div style="display:flex;justify-content:center;">
    <div style="background:#2ca02c;color:#fff;border-radius:8px;padding:14px 28px;text-align:center;min-width:420px;box-shadow:0 2px 8px rgba(44,160,44,0.22);">
      <div style="font-weight:700;font-size:14px;">6. submit_sample()</div>
      <div style="font-size:12px;opacity:0.9;margin-top:4px;">POST to EMBL-EBI BioSamples API</div>
    </div>
  </div>

  <!-- Arrow: submit to result (green) -->
  <div style="display:flex;flex-direction:column;align-items:center;">
    <div style="width:3px;height:20px;background:#2ca02c;"></div>
    <div style="font-size:10px;color:#2ca02c;font-weight:600;">API response</div>
    <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #2ca02c;"></div>
  </div>

  <!-- STEP 7: Success -->
  <div style="display:flex;justify-content:center;">
    <div style="background:linear-gradient(135deg,#1a7a6e,#2ca02c);color:#fff;border-radius:8px;padding:14px 28px;text-align:center;min-width:420px;box-shadow:0 2px 12px rgba(26,122,110,0.25);">
      <div style="font-weight:700;font-size:14px;">7. Success</div>
      <div style="font-size:12px;opacity:0.9;margin-top:4px;">Real accession assigned by EMBL-EBI</div>
      <div style="font-size:11px;margin-top:4px;opacity:0.8;">e.g. SAMEA122005222 &nbsp;|&nbsp; SAMEA122005223</div>
    </div>
  </div>

  <!-- COLOR LEGEND -->
  <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;padding:12px 0 0 0;margin-top:14px;border-top:1px solid #e0e0e0;">
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#1f77b4;"></div><span style="font-size:11px;color:#444;">User Input</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#9467bd;"></div><span style="font-size:11px;color:#444;">Intelligence</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#d62728;"></div><span style="font-size:11px;color:#444;">Missing Fields</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#2ca02c;"></div><span style="font-size:11px;color:#444;">Submit / Success</span></div>
  </div>

</div>
"""

# Render diagram 2 as an HTML component
components.html(DIAGRAM_2_HTML, height=900, scrolling=False)

# Divider before diagram 3
st.divider()

# ================================================================
# DIAGRAM 3 — Repository File Structure (HTML/CSS)
# ================================================================

# Section heading for diagram 3
st.subheader("Diagram 3 — Repository File Structure")

# Explanation paragraph for diagram 3
st.write(
    "The repository is organised into four top-level directories: "
    "src/ contains all server and tool logic, ui/ contains the "
    "Streamlit interface, tests/ contains the pytest suite, "
    "and checklists/ holds the BioSamples validation JSON files. "
    "Each file is colored by its architectural layer."
)

# Full HTML string for diagram 3 — indented file tree with layer colors
DIAGRAM_3_HTML = """
<style>
  .tree { font-family:'Courier New',monospace; font-size:13px; line-height:1.9; color:#333; }
  .tree-folder { font-weight:700; }
  .tree-desc { font-size:11px; font-style:italic; margin-left:6px; }
  .c-root { color:#1f4e79; }
  .c-server { color:#2ca02c; }
  .c-tool-std { color:#ff7f0e; }
  .c-tool-ai { color:#d62728; }
  .c-intel { color:#9467bd; }
  .c-ui { color:#1f77b4; }
  .c-test { color:#7f7f7f; }
  .c-infra { color:#555; }
  .badge { display:inline-block; padding:1px 7px; border-radius:4px; color:#fff; font-size:10px; font-family:Arial,sans-serif; font-weight:600; margin-left:6px; vertical-align:middle; }
</style>
<div style="font-family:Arial,sans-serif;max-width:860px;margin:0 auto;background:#fafafa;padding:28px 24px 18px 24px;border-radius:14px;box-shadow:0 2px 16px rgba(0,0,0,0.07);">
<div class="tree">

<span class="tree-folder c-root">biosamples-mcp/</span><br>

<span class="c-root">├── </span><span class="tree-folder c-root">src/</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-server">├── server.py</span><span class="badge" style="background:#2ca02c;">Server</span><span class="tree-desc c-server">FastAPI REST server, port 8000</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-server">├── mcp_server.py</span><span class="badge" style="background:#2ca02c;">Server</span><span class="tree-desc c-server">FastMCP stdio server</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-server">├── biosamples_client.py</span><span class="badge" style="background:#2ca02c;">Server</span><span class="tree-desc c-server">All EMBL-EBI API calls</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-intel">├── nlp_parser.py</span><span class="badge" style="background:#9467bd;">Intel</span><span class="tree-desc c-intel">Text to metadata extraction</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-intel">├── checklist_validator.py</span><span class="badge" style="background:#9467bd;">Intel</span><span class="tree-desc c-intel">Field validation + questions</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-root">└── </span><span class="tree-folder c-root">tools/</span><br>
<span class="c-root">│&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; </span><span class="c-tool-std">├── search_tool.py</span><span class="badge" style="background:#ff7f0e;">Tool</span><br>
<span class="c-root">│&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; </span><span class="c-tool-std">├── fetch_tool.py</span><span class="badge" style="background:#ff7f0e;">Tool</span><br>
<span class="c-root">│&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; </span><span class="c-tool-std">├── submit_tool.py</span><span class="badge" style="background:#ff7f0e;">Tool</span><br>
<span class="c-root">│&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; </span><span class="c-tool-ai">├── smart_submit_tool.py</span><span class="badge" style="background:#d62728;">AI</span><br>
<span class="c-root">│&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; </span><span class="c-tool-ai">└── natural_search_tool.py</span><span class="badge" style="background:#d62728;">AI</span><br>

<span class="c-root">├── </span><span class="tree-folder c-root">ui/</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-ui">├── app.py</span><span class="badge" style="background:#1f77b4;">UI</span><span class="tree-desc c-ui">Main Streamlit home page</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-root">├── </span><span class="tree-folder c-root">pages/</span><br>
<span class="c-root">│&nbsp;&nbsp; │&nbsp;&nbsp; </span><span class="c-ui">├── 00_Architecture.py</span><span class="badge" style="background:#1f77b4;">UI</span><br>
<span class="c-root">│&nbsp;&nbsp; │&nbsp;&nbsp; </span><span class="c-ui">├── 01_search.py</span><span class="badge" style="background:#1f77b4;">UI</span><br>
<span class="c-root">│&nbsp;&nbsp; │&nbsp;&nbsp; </span><span class="c-ui">├── 02_fetch.py</span><span class="badge" style="background:#1f77b4;">UI</span><br>
<span class="c-root">│&nbsp;&nbsp; │&nbsp;&nbsp; </span><span class="c-ui">├── 03_ai_submit.py</span><span class="badge" style="background:#1f77b4;">UI</span><br>
<span class="c-root">│&nbsp;&nbsp; │&nbsp;&nbsp; </span><span class="c-ui">└── 04_nl_search.py</span><span class="badge" style="background:#1f77b4;">UI</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-root">└── </span><span class="tree-folder c-root">utils/</span><br>
<span class="c-root">│&nbsp;&nbsp; &nbsp;&nbsp;&nbsp; </span><span class="c-ui">└── api_client.py</span><span class="badge" style="background:#1f77b4;">UI</span><span class="tree-desc c-ui">REST client for all pages</span><br>

<span class="c-root">├── </span><span class="tree-folder c-root">tests/</span><span class="tree-desc c-test">21 tests, all passing</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-test">├── test_search.py</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-test">├── test_fetch.py</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-test">├── test_submit.py</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-test">├── test_nlp_parser.py</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-test">├── test_checklist_validator.py</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-test">├── test_smart_submit.py</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-test">└── test_natural_search.py</span><br>

<span class="c-root">├── </span><span class="tree-folder c-root">checklists/</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-intel">├── default.json</span><span class="badge" style="background:#9467bd;">Intel</span><span class="tree-desc c-intel">Minimum: organism required</span><br>
<span class="c-root">│&nbsp;&nbsp; </span><span class="c-intel">└── human_sample.json</span><span class="badge" style="background:#9467bd;">Intel</span><span class="tree-desc c-intel">Stricter: tissue + date required</span><br>

<span class="c-infra">├── Dockerfile</span><span class="tree-desc c-infra">Container deployment</span><br>
<span class="c-infra">├── docker-compose.yml</span><span class="tree-desc c-infra">Single-command startup</span><br>
<span class="c-infra">└── .github/workflows/ci.yml</span><span class="tree-desc c-infra">GitHub Actions CI</span><br>

</div>

  <!-- COLOR LEGEND -->
  <div style="display:flex;justify-content:center;gap:16px;flex-wrap:wrap;padding:12px 0 0 0;margin-top:8px;border-top:1px solid #e0e0e0;">
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#2ca02c;"></div><span style="font-size:11px;color:#444;">Server Layer</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#ff7f0e;"></div><span style="font-size:11px;color:#444;">Standard Tools</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#d62728;"></div><span style="font-size:11px;color:#444;">AI-Powered Tools</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#9467bd;"></div><span style="font-size:11px;color:#444;">Intelligence Layer</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#1f77b4;"></div><span style="font-size:11px;color:#444;">Streamlit UI</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#7f7f7f;"></div><span style="font-size:11px;color:#444;">Tests</span></div>
    <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:#555;"></div><span style="font-size:11px;color:#444;">Infrastructure</span></div>
  </div>

</div>
"""

# Render diagram 3 as an HTML component
components.html(DIAGRAM_3_HTML, height=820, scrolling=False)

# Divider before component table
st.divider()

# --- Component Descriptions section ---

# Section heading
st.subheader("Component Descriptions")

# Component table — one row per key module
st.markdown("""
| Component | File | Purpose |
|-----------|------|---------|
| REST Server | `src/server.py` | HTTP API for curl, Docker, Streamlit |
| MCP Server | `src/mcp_server.py` | stdio server for Claude Desktop |
| BioSamples Client | `src/biosamples_client.py` | All EMBL-EBI API calls |
| NLP Parser | `src/nlp_parser.py` | Extract metadata from plain text |
| Checklist Validator | `src/checklist_validator.py` | Validate against BioSamples checklists |
| Streamlit UI | `ui/app.py` | Visual interface for demos |
""")

# Divider before live evidence
st.divider()

# --- Live Evidence section ---

# Section heading
st.subheader("Live Evidence")

# One sentence introducing the confirmed accessions
st.write(
    "The following samples were submitted to the EMBL-EBI BioSamples "
    "production database during development, confirming end-to-end functionality:"
)

# Link to the first confirmed accession
st.markdown(
    "**SAMEA122005222** — Human blood sample, Germany  \n"
    "[View on BioSamples](https://www.ebi.ac.uk/biosamples/samples/SAMEA122005222)"
)

# Link to the second confirmed accession
st.markdown(
    "**SAMEA122005223** — Human liver biopsy, London, cirrhosis  \n"
    "[View on BioSamples](https://www.ebi.ac.uk/biosamples/samples/SAMEA122005223)"
)
