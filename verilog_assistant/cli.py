"""Command-line entry point.

Usage:
    python -m verilog_assistant.cli "a 4-bit up counter with synchronous reset"
"""

from __future__ import annotations

import sys

from verilog_assistant.agent.loop import generate_rtl
from verilog_assistant.config import settings
from verilog_assistant.llm.client import LLMError
from verilog_assistant.sim.simulator import ToolchainError, toolchain_available


def main() -> int:
    if len(sys.argv) < 2:
        print('usage: python -m verilog_assistant.cli "<spec>"')
        return 2

    spec = " ".join(sys.argv[1:])

    if not settings.has_api_key:
        print("[error] No API key. Copy .env.example to .env and set DEEPSEEK_API_KEY.")
        return 3
    if not toolchain_available():
        print("[error] Icarus Verilog not found. Install iverilog + vvp and retry.")
        return 4

    try:
        result = generate_rtl(spec)
    except (LLMError, ToolchainError) as exc:
        print(f"[error] {exc}")
        return 1

    print("=" * 60)
    print(f"SPEC: {result.spec}")
    print(f"RESULT: {'PASS' if result.passed else 'FAIL'} after {result.attempts} attempt(s)")
    print("=" * 60)
    print("\n--- MODULE ---\n")
    print(result.rtl)
    print("\n--- TESTBENCH ---\n")
    print(result.testbench)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
