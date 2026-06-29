"""Wrap Icarus Verilog (`iverilog` + `vvp`) to compile and run an
(RTL, testbench) pair and report a structured pass/fail result.

Convention: a self-checking testbench should print the literal token
``TEST PASSED`` on success and ``TEST FAILED`` on any mismatch. The agent's
prompts enforce this so the loop can judge correctness automatically.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

PASS_TOKEN = "TEST PASSED"
FAIL_TOKEN = "TEST FAILED"


class ToolchainError(RuntimeError):
    """Raised when the Icarus Verilog toolchain is not available."""


@dataclass
class SimResult:
    """Outcome of compiling and running an (RTL, testbench) pair."""

    passed: bool
    compiled: bool
    stdout: str
    stderr: str

    @property
    def log(self) -> str:
        parts = []
        if self.stdout.strip():
            parts.append("--- stdout ---\n" + self.stdout.strip())
        if self.stderr.strip():
            parts.append("--- stderr ---\n" + self.stderr.strip())
        return "\n\n".join(parts) if parts else "(no output)"


def toolchain_available() -> bool:
    """True if both `iverilog` and `vvp` are on PATH."""
    return shutil.which("iverilog") is not None and shutil.which("vvp") is not None


def _require_toolchain() -> None:
    if not toolchain_available():
        raise ToolchainError(
            "Icarus Verilog not found on PATH. Install it (iverilog + vvp) and "
            "reopen your terminal. Windows: https://bleyer.org/icarus/"
        )


def compile_and_run(rtl: str, testbench: str, timeout: float = 20.0) -> SimResult:
    """Compile `rtl` + `testbench` with iverilog and run with vvp.

    Returns a SimResult. `passed` is True only if compilation succeeds, the run
    does not error, the PASS token is present, and the FAIL token is absent.
    """
    _require_toolchain()

    with tempfile.TemporaryDirectory(prefix="vassist_") as tmp:
        tmp_path = Path(tmp)
        rtl_file = tmp_path / "dut.v"
        tb_file = tmp_path / "tb.v"
        out_file = tmp_path / "sim.out"
        rtl_file.write_text(rtl, encoding="utf-8")
        tb_file.write_text(testbench, encoding="utf-8")

        compile_proc = subprocess.run(
            ["iverilog", "-g2012", "-o", str(out_file), str(rtl_file), str(tb_file)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if compile_proc.returncode != 0:
            return SimResult(
                passed=False,
                compiled=False,
                stdout=compile_proc.stdout,
                stderr=compile_proc.stderr or "Compilation failed.",
            )

        try:
            run_proc = subprocess.run(
                ["vvp", str(out_file)],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return SimResult(
                passed=False,
                compiled=True,
                stdout="",
                stderr=f"Simulation timed out after {timeout}s (possible infinite loop / missing $finish).",
            )

        stdout = run_proc.stdout
        stderr = run_proc.stderr
        passed = (
            run_proc.returncode == 0
            and PASS_TOKEN in stdout
            and FAIL_TOKEN not in stdout
        )
        return SimResult(passed=passed, compiled=True, stdout=stdout, stderr=stderr)


def _cli() -> int:
    """Standalone check: `python -m verilog_assistant.sim.simulator rtl.v tb.v`."""
    if len(sys.argv) != 3:
        print("usage: python -m verilog_assistant.sim.simulator <rtl.v> <tb.v>")
        return 2
    rtl = Path(sys.argv[1]).read_text(encoding="utf-8")
    tb = Path(sys.argv[2]).read_text(encoding="utf-8")
    try:
        result = compile_and_run(rtl, tb)
    except ToolchainError as exc:
        print(f"[toolchain] {exc}")
        return 3
    print(result.log)
    print()
    print("RESULT:", "PASS" if result.passed else "FAIL")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
