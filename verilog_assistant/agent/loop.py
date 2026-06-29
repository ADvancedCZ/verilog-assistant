"""Agent loop: spec -> generate RTL -> generate testbench -> simulate ->
on failure, feed the simulation errors back to the model and retry.

This closed loop (generate + simulate + self-correct) is the core value of
the project: it proves correctness automatically instead of just printing code.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from verilog_assistant.config import settings
from verilog_assistant.llm.client import LLMClient
from verilog_assistant.prompts import templates
from verilog_assistant.sim.simulator import SimResult, compile_and_run


@dataclass
class AgentResult:
    """Final output of a run."""

    spec: str
    rtl: str
    testbench: str
    passed: bool
    attempts: int
    transcript: list[str] = field(default_factory=list)


def generate_rtl(spec: str, client: LLMClient | None = None, max_retries: int | None = None) -> AgentResult:
    """Run the full generate/simulate/self-correct loop for one spec."""
    client = client or LLMClient()
    max_retries = settings.max_retries if max_retries is None else max_retries
    transcript: list[str] = []

    # 1. Generate the initial module.
    rtl_raw = client.generate(templates.codegen_prompt(spec), system=templates.SYSTEM)
    rtl = templates.extract_code(rtl_raw)
    transcript.append(f"[gen rtl]\n{rtl}")

    # 2. Generate a self-checking testbench (kept fixed across retries).
    tb_raw = client.generate(templates.testbench_prompt(spec, rtl), system=templates.SYSTEM)
    testbench = templates.extract_code(tb_raw)
    transcript.append(f"[gen testbench]\n{testbench}")

    # 3. Simulate, and self-correct the RTL on failure.
    result: SimResult = compile_and_run(rtl, testbench)
    attempts = 1
    transcript.append(f"[sim attempt {attempts}] passed={result.passed}\n{result.log}")

    while not result.passed and attempts <= max_retries:
        fixed_raw = client.generate(
            templates.fix_prompt(spec, rtl, testbench, result.log),
            system=templates.SYSTEM,
        )
        rtl = templates.extract_code(fixed_raw)
        attempts += 1
        result = compile_and_run(rtl, testbench)
        transcript.append(f"[sim attempt {attempts}] passed={result.passed}\n{result.log}")

    return AgentResult(
        spec=spec,
        rtl=rtl,
        testbench=testbench,
        passed=result.passed,
        attempts=attempts,
        transcript=transcript,
    )
