# Verilog / RTL Assistant

An LLM agent that turns a natural-language hardware spec into **synthesizable Verilog** plus a **self-checking testbench**, then **simulates it and self-corrects** on failure. The closed loop (generate -> simulate -> fix) proves correctness automatically instead of just printing code.

Built with Python + DeepSeek (any OpenAI-compatible endpoint, e.g. Qwen) and Icarus Verilog.

## How it works

```
spec --> [LLM] gen RTL --> [LLM] gen self-checking testbench
                                  |
                                  v
                          [iverilog + vvp] simulate
                                  |
                       pass? --yes--> return RTL + TB
                          |
                          no
                          v
                 [LLM] read errors, fix RTL (retry <= N) --> simulate again
```

## Setup

### Prerequisites (install once per machine)

1. **Python 3.12** from python.org. During install, check "Add python.exe to PATH" and "py launcher".
2. **Icarus Verilog** (`iverilog` + `vvp` on PATH). Windows: https://bleyer.org/icarus/ (check "Add to PATH" in the installer). Optional: **GTKWave** to view `sim.vcd` waveforms.

### Environment (reproducible on any computer)

This repo uses a `.venv` virtual environment that is **not** committed to git. On each
machine you only commit/clone the source + `requirements.txt`, then recreate the venv.

**Windows (PowerShell):**
```
./setup.ps1
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```
bash setup.sh
source .venv/bin/activate
```

The script creates `.venv` with Python 3.12, installs dependencies, and copies
`.env.example` to `.env`. Then add your DeepSeek key to `.env` (get one at
https://platform.deepseek.com).

**Manual alternative:**
```
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

### Working across multiple computers (git)

```
git init
git add .
git commit -m "Initial Verilog Assistant scaffold"
# create an empty repo on GitHub/Gitee, then:
git remote add origin <your-repo-url>
git push -u origin main
```

On another computer: `git clone <url>`, then run the setup script above. The
`.venv` and `.env` are git-ignored, so each machine recreates them locally and
your API key never leaves your machine.

## Run

**Simulator only (no API key needed) - the Week 1 spike:**
```
python -m verilog_assistant.sim.simulator examples/counter.v examples/counter_tb.v
```
Expected: prints the run log and `RESULT: PASS`.

**Tests:**
```
pytest -q
```
(Simulator tests skip automatically if Icarus Verilog is not installed.)

**Full agent (needs API key + Icarus Verilog):**
```
python -m verilog_assistant.cli "a 4-bit up counter with synchronous reset"
```

**Web UI:**
```
streamlit run app/streamlit_app.py
```

## Project layout

```
verilog_assistant/
  config.py            # env / settings
  llm/client.py        # provider-agnostic LLM client (DeepSeek/Qwen/OpenAI)
  prompts/templates.py # codegen, testbench, error-fix prompts + code extraction
  sim/simulator.py     # Icarus Verilog compile + run -> pass/fail
  agent/loop.py        # generate -> simulate -> self-correct loop
  cli.py               # command-line entry point
app/streamlit_app.py   # web UI
examples/              # hand-written counter + self-checking testbench
tests/                 # simulator tests (skip if no toolchain)
```

## Results

Run the agent over the open **VerilogEval** / **RTLLM** benchmarks and record pass-rates here:

| Setting                | pass@1 |
|------------------------|--------|
| No self-correction     | TBD    |
| + self-correction      | TBD    |
| + RAG (planned)        | TBD    |

## Roadmap

- [x] Simulation wrapper + self-checking example (Week 1)
- [x] LLM codegen + testbench generation
- [x] Self-correction loop + CLI + Streamlit UI
- [ ] RAG over a Verilog patterns corpus
- [ ] VerilogEval / RTLLM evaluation harness with pass-rate numbers
- [ ] VS Code extension front-end
