"""Tests for prompt contracts that affect generated simulation behavior."""

from verilog_assistant.prompts import templates


def test_testbench_prompt_requires_race_free_sequential_stimulus():
    prompt = templates.testbench_prompt(
        "a 4-bit up counter with synchronous reset",
        "module counter(input clk, input rst, output reg [3:0] count); endmodule",
    )

    assert "avoid clock-edge race conditions" in prompt
    assert "inactive clock edge" in prompt
    assert "small delay following the active clock edge" in prompt
    assert "cycle-aligned with the DUT" in prompt
    assert "do not insert unaccounted clock cycles" in prompt
    assert "first advance the expected/reference state" in prompt
    assert "compare the DUT output against the advanced expected value" in prompt
    assert "if reset is deasserted before an active clock edge" in prompt
    assert "Do not expect the reset value after that edge" in prompt
