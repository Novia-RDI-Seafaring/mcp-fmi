<p align="center">
  <a href="https://novia.fi"><img src="./public/mcp_fmu_logo.png" alt="MCP-FMU" width="100">
</a>
</p>

<p align="center">
    <b>Model Context Protocol - Functional Mockup Units</b> <br />
    Makes your simulation models available as tools for AI-based agents.
</p>

<p align="center">
  <a href="https://www.novia.fi/" target="_blank">
      Novia UAS
  </a>|
  <a href="https://www.virtualseatrial.fi/" target="_blank">
      Project
  </a>|
  <a href="https://github.com/mcp-fmu/chroma/blob/master/LICENSE" target="_blank">
      License
  </a>
</p>

# MCP - Functional Mockup Units
This package integrates FMU simulation models as tools for LLM-based agents through the MCP. This is an unofficial MCP-integration of the [FMPy](https://fmpy.readthedocs.io/en/latest/) package.

[The Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open standard for integrating large language model (LLM) applications with external data sources and tools. It provides a standardized way to supply LLMs with the context they need for advanced reasoning and interaction.

[The Functional Mockup Interface (FMI)](https://fmi-standard.org/) is a widely adopted standard for exchanging and co-simulating dynamic models across simulation platforms. **A Functional Mockup Unit (FMU)** is a file containing a simulation model that adheres to the FMI standard. 

## Features
- **Instantiate simulations** from chat interfaces.
- **Simulation models as tools** for AI agents. 
- **Generate input signals from natural language**
-**Visualize simulation results** as itnerractive artifacts in Claude Desktop or in browser.

## Implemented tools
List of implemented tools:
- `fmu_information_tool` retrieves information about the available FMU models.
- `simulate_tool`simulates a single FMU model with default prameters and input signals. Returns the simulated outputs.
- `simulate_with_input_tool` simulates a single FMU model with the specified input signals. Returns the simulated outputs.
- `create_signal_tool` generates an input-sequence object for a single input.
- `merge_signals_tool` merges multiple signel objects that can be used as an input for a simulation.
- `show_results_in_browser_tool` visualizes simulation results in browser.

## Prerequisites

- Python 3.13 or higher
- [uv](https://docs.astral.sh/uv/pip/packages/) package manager
- Claude Desktop (for desktop integration)

## Installation

1. Create and activate a virtual environment:
```bash
# Create venv with uv
uv venv

# Activate on macOS/Linux
source .venv/bin/activate

# Activate on Windows
.venv\Scripts\activate
```

2. Install dependencies:
```bash
# Make sure you're in the project root directory
uv pip install -e .
```

Then add MCP to your project dependencies:
```cmd
uv add "mcp[cli]"
```

To run the mcp command with uv:
```cmd
uv run mcp
```

## Run the MCP-FMU server
Run the server and the MCP Inspector:
```bash
uv run --with mcp --with mcp-fmu --with python-dotenv --with fmpy --with numpy --with pydantic mcp dev src/mcp_fmu/server.py
```

## Claude Desktop Integration
Update the `claude_desktop_config.json` file:
```json
{
  "mcpServers": {
    "MCP-FMU Server": {
      "command": "LOCAL_PATCH_TO_UV\\uv.EXE",
      "args": [
        "run",
        "--with", "dash",
        "--with", "fmpy",
        "--with", "mcp[cli]",
        "--with", "pydantic",
        "--with", "python-dotenv",
        "--with", "numpy",
        "mcp",
        "run",
        "LOCAL_PATH_TO_PROJECT\\mcp-fmu\\src\\mcp_fmu\\server.py"
      ],
      "env": {
        "PYTHONPATH": "LOCAL_PATH_TO_PROJECT\\mcp-fmu\\src"
      }
    }
  }
}

```

## Example use
Example queries:
- What simulation models do you have available?
- Give me informaiton of input and output signals of model `model name`.
- Who created the model `model name` and when was it last updated?
- Make a step-change in input `input name` at 60s. Keep the other inputs constant with default values.
- Simulate `model name` with generated inputs.

## Future work
List of tools to be implemented:
- `show_results_as_artifact_tool` visualized simulation results as interractive artifacts in Claude Desktop.
- `co_simulate_tool` co-simulates multiple FMU models.

## Acknowledgements
This work was done in the Business Finland funded project [Virtual Sea Trial](https://virtualseatrial.fi)
