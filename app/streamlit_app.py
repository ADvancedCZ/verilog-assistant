"""Minimal Streamlit UI for the Verilog Assistant.

Run:  streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the package importable when run via `streamlit run`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st  # noqa: E402

from verilog_assistant.agent.loop import generate_rtl  # noqa: E402
from verilog_assistant.config import settings  # noqa: E402
from verilog_assistant.llm.client import LLMError  # noqa: E402
from verilog_assistant.sim.simulator import ToolchainError, toolchain_available  # noqa: E402

st.set_page_config(page_title="Verilog Assistant", page_icon="chip", layout="wide")
st.title("Verilog / RTL Assistant")
st.caption("Describe a digital block -> get synthesizable Verilog + a self-checking testbench, auto-simulated and self-corrected.")

with st.sidebar:
    st.subheader("Status")
    st.write("API key:", "set" if settings.has_api_key else "MISSING (.env)")
    st.write("Icarus Verilog:", "found" if toolchain_available() else "MISSING")
    st.write("Model:", settings.model)

spec = st.text_area(
    "Specification",
    value="A 4-bit up counter with synchronous active-high reset.",
    height=120,
)

if st.button("Generate", type="primary"):
    if not settings.has_api_key:
        st.error("No API key. Copy .env.example to .env and set DEEPSEEK_API_KEY.")
    elif not toolchain_available():
        st.error("Icarus Verilog not found. Install iverilog + vvp and reload.")
    else:
        with st.spinner("Generating and simulating..."):
            try:
                result = generate_rtl(spec)
            except (LLMError, ToolchainError) as exc:
                st.error(str(exc))
                st.stop()

        if result.passed:
            st.success(f"PASS after {result.attempts} attempt(s)")
        else:
            st.warning(f"FAIL after {result.attempts} attempt(s) - inspect the transcript below")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Module")
            st.code(result.rtl, language="verilog")
        with col2:
            st.subheader("Testbench")
            st.code(result.testbench, language="verilog")

        with st.expander("Transcript (generation + simulation log)"):
            for step in result.transcript:
                st.text(step)
