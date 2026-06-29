"""Tests for the simulator wrapper. Skips gracefully if Icarus Verilog
is not installed so the suite is green even before toolchain setup."""

from pathlib import Path

import pytest

from verilog_assistant.sim.simulator import compile_and_run, toolchain_available

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


requires_toolchain = pytest.mark.skipif(
    not toolchain_available(),
    reason="Icarus Verilog (iverilog/vvp) not on PATH",
)


@requires_toolchain
def test_counter_example_passes():
    rtl = (EXAMPLES / "counter.v").read_text(encoding="utf-8")
    tb = (EXAMPLES / "counter_tb.v").read_text(encoding="utf-8")
    result = compile_and_run(rtl, tb)
    assert result.compiled, result.log
    assert result.passed, result.log


@requires_toolchain
def test_broken_rtl_fails():
    # Counter that never counts -> testbench should report failure.
    broken_rtl = """
    module counter (input wire clk, input wire rst, output reg [3:0] count);
        always @(posedge clk) count <= 4'd0;
    endmodule
    """
    tb = (EXAMPLES / "counter_tb.v").read_text(encoding="utf-8")
    result = compile_and_run(broken_rtl, tb)
    assert result.compiled
    assert not result.passed
