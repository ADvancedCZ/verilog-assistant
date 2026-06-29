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

### Quickstart on a new computer (do this in order)

1. **Install Python 3.12** (see Prerequisites below).
2. **Install Icarus Verilog v12** (see Prerequisites below).
3. **Clone the repo:**
   ```
   git clone <your-repo-url>
   cd verilog-assistant
   ```
4. **Create the environment:**
   ```
   ./setup.ps1                       # Windows (PowerShell)
   .\.venv\Scripts\Activate.ps1
   ```
   (macOS/Linux: `bash setup.sh` then `source .venv/bin/activate`)
5. **Add your DeepSeek API key** to the `.env` file that setup created (`DEEPSEEK_API_KEY=...`).
6. **Verify it works (no key needed for this):**
   ```
   python -m verilog_assistant.sim.simulator examples/counter.v examples/counter_tb.v
   pytest -q
   ```
   Expect `RESULT: PASS` and all tests passing. If `iverilog` is "not recognized", see the PATH note below.

### Prerequisites (install once per machine)

1. **Python 3.12** from python.org (https://www.python.org/downloads/release/python-3129/).
   During install, **check "Add python.exe to PATH" and "py launcher"**.
   Verify in a NEW terminal: `py -3.12 --version`.
2. **Icarus Verilog v12** (the Verilog simulator: `iverilog` + `vvp`).
   - Windows: download from https://bleyer.org/icarus/ . **Install v12** (not v11) -- the
     project compiles with `-g2012` which needs v12's Verilog-2012 support.
   - During install, **check "Add executable folder(s) to the user PATH"**.
   - Verify in a NEW terminal: `iverilog -V` (should print version 12.0).
3. **GTKWave** (optional, recommended) to view `sim.vcd` waveforms. Some Icarus
   installers bundle it; otherwise install separately and it appears as `gtkwave`.

> **PATH gotcha:** after installing Python or Icarus, **open a brand-new terminal
> (or restart the IDE)** before running commands. Already-open terminals keep the
> old PATH and will report "command not recognized" even though install succeeded.
> On Windows you can confirm the Icarus folder is on PATH with:
> `[Environment]::GetEnvironmentVariable("Path","User")`

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

**First time (push from this computer):** the repo is already `git init`-ed and
committed locally. Create an empty repo on GitHub or Gitee (Gitee is faster from
China), then connect and push:
```
git remote add origin <your-repo-url>
git push -u origin main
```

**On another computer (continue work):**
```
git clone <your-repo-url>
cd verilog-assistant
./setup.ps1                  # recreate .venv + install deps
.\.venv\Scripts\Activate.ps1
# then add your DeepSeek key to .env
```
You still need Python 3.12 + Icarus Verilog installed on that machine (see
Prerequisites). The `.venv` and `.env` are git-ignored, so each machine recreates
them locally and **your API key never leaves your machine / never goes to git**.

**Saving your work each session:**
```
git add -A
git commit -m "describe what you changed"
git push
```

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
