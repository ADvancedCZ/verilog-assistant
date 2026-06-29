"""System/user prompt templates and a helper to extract code from responses."""

from __future__ import annotations

import re

from verilog_assistant.sim.simulator import FAIL_TOKEN, PASS_TOKEN

SYSTEM = (
    "You are an expert digital design engineer. You write clean, synthesizable "
    "Verilog-2001/2012. You never use non-synthesizable constructs in design "
    "modules. You output only code inside a single ```verilog code block, with "
    "no prose before or after."
)


def codegen_prompt(spec: str) -> str:
    return (
        "Write a synthesizable Verilog module that implements the following "
        "specification. Use synchronous logic with a single clock where "
        "sequential behavior is needed. Choose clear port names.\n\n"
        f"SPECIFICATION:\n{spec}\n\n"
        "Output ONLY the module in one ```verilog block."
    )


def testbench_prompt(spec: str, rtl: str) -> str:
    return (
        "Write a self-checking Verilog testbench for the module below.\n\n"
        "Requirements:\n"
        f"- Print the exact token \"{PASS_TOKEN}\" if all checks pass.\n"
        f"- Print the exact token \"{FAIL_TOKEN}\" if any check fails.\n"
        "- Drive a clock if the design is sequential and call $finish at the end.\n"
        "- Compare outputs against an independently computed expected value.\n"
        "- Include $dumpfile(\"sim.vcd\"); $dumpvars; for waveform debugging.\n\n"
        f"SPECIFICATION:\n{spec}\n\n"
        f"MODULE UNDER TEST:\n```verilog\n{rtl}\n```\n\n"
        "Output ONLY the testbench in one ```verilog block."
    )


def fix_prompt(spec: str, rtl: str, testbench: str, sim_log: str) -> str:
    return (
        "Your Verilog module failed its testbench. Fix the MODULE so the "
        "testbench passes. Do not change the testbench. Keep it synthesizable.\n\n"
        f"SPECIFICATION:\n{spec}\n\n"
        f"CURRENT MODULE:\n```verilog\n{rtl}\n```\n\n"
        f"TESTBENCH:\n```verilog\n{testbench}\n```\n\n"
        f"SIMULATION OUTPUT (errors):\n{sim_log}\n\n"
        "Output ONLY the corrected module in one ```verilog block."
    )


_CODE_BLOCK = re.compile(r"```(?:verilog|systemverilog|v)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def extract_code(text: str) -> str:
    """Pull Verilog out of a fenced code block, or return the trimmed text."""
    matches = _CODE_BLOCK.findall(text)
    if matches:
        return matches[0].strip()
    return text.strip()
