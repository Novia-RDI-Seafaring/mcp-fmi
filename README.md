<p align="center">
  <a href="https://novia.fi"><img src="public/mcp_fmi_logo.svg" alt="MCP-FMI" width="100">
</a>
</p>

<p align="center">
    <b>Model Context Protocol - Functional Mock-up Interface</b> <br />
    Makes your simulation models available as tools for LLM-based agents.
</p>

<p align="center">
  <a href="https://www.novia.fi/" target="_blank">
      Novia UAS
  </a>|
  <a href="https://www.virtualseatrial.fi/" target="_blank">
      Research Project
  </a>|
  <a href="mailto:mikael.manngard@novia.fi?subject=MCP-FMI:">Contact</a>

</p>
<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.11%2B-blue" alt="Python Version">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/github/license/Novia-RDI-Seafaring/mcp-fmi" alt="License: MIT">
  </a>
  <a href="https://www.businessfinland.fi/">
    <img src="https://img.shields.io/badge/Funded%20by-Business%20Finland-blue" alt="Funded by Business Finland">
  </a>
</p>

# MCP-FMI
This is an unofficial MCP-integration of the [FMPy](https://fmpy.readthedocs.io/en/latest/) package.

## Table of Content
1. [Overview](#overview)  
   1.1 [Features](#features)  
   1.2 [Implemented Tools](#implemented-tools)  
   1.3 [Standards](#standards)  
2. [Prerequisites](#prerequisites)  
3. [Claude Desktop Integration](#claude-desktop-integration)
5. [For Developers](#for-developers) 
4. [Example Usage](#example-usage)   
6. [Future Work](#future-work)  
7. [Citation](#citation)  
8. [Acknowledgements](#acknowledgements)  
9. [License](#license)  


## Overview
This package integrates FMU simulation models as tools for LLM-based agents through the MCP. By allowing simulation models to be accessed and orchestrated directly from chat interfaces, simulation models become accessible to virtually anyone. This means simulation capabilities can be shared across teams and organizations, including with non-experts, bringing the benefits of simulation to everyone you collaborate with.

<p align="center">
  <img src="public/tools.svg" alt="MCP-FMI Tools" width="100%">
</p>

### Features
- **💬 Manage simulations** from chat interfaces.
- **🛠️ Use simulation models as tools** for LLM-based agents. 
- **📈 Generate input signals** for simulations from natural language.
- **📊 Visualize simulation results** in browser.

### Implemented tools
- `fmu_information_tool` retrieves information about the available FMU models.
- `simulate_tool`simulates a single FMU model with default prameters and input signals. Returns the simulated outputs.
- `simulate_with_input_tool` simulates a single FMU model with the specified input signals. Returns the simulated outputs.
- `create_signal_tool` generates an input-sequence object for a single input.
- `merge_signals_tool` merges multiple signel objects that can be used as an input for a simulation.
- `show_results_in_browser_tool` visualizes simulation results in browser.

### Standards
This package bridges two standards:

[The Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open protocol that standardizes how applications can provide context to Large Language Models (LLMs). MCP helps when integrating data and tools to LLM-based agents. 

[The Functional Mockup Interface (FMI)](https://fmi-standard.org/) is a free standard that defines a container and interface to exchange dynamic simulation models across simulation platforms. A **Functional Mockup Unit (FMU)** is a file containing a simulation model that adheres to the FMI standard. 

## Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/pip/packages/) package manager
- Claude Desktop (for desktop integration)

## Usage with Claude Desktop
Update the `claude_desktop_config.json` file with:
```json
{
  "mcpServers": {
    "MCP-FMI Server": {
      "command": "uvx",
      "args": ["mcp-fmi",  "/path/to/folder/with/fmu/files"],
    }
  }
}

```

## For developers
Intructions how to run the package in editable mode: [CONTRIBUTING.md](CONTRIBUTING.md).

## Example usage

Example natural-language queries:
- What simulation models do you have available?
- Please provide information about the model and its signals.
- Who created the model, and when was it last updated?
- Make a step change in the input `input_name` at 60s. Keep the other inputs constant with their default values.
- Simulate `model_name` with the generated inputs.

Short demonstration in Claude Desktop:
<p align="center">
  <img src="public/mcp-fmi-short.gif" alt="MCP-FMI Claude" width="100%">
</p>

## Future work
List of features to be implemented:
- Better support for Windows/Linux/MacOS FMU models.
- `co_simulate_tool` co-simulates multiple FMU models.
- Integration for [OpenWebUI](https://openwebui.com/).
- `show_results_as_artifact_tool` return simulation results as interractive artifacts.
- Features for exporting results.

## Citation
If you use this package in your research, please cite it using the following BibTeX entry:

```bibtex
@misc{MCP-FMI,
  author = {Mikael Manngård, Christoffer Björkskog},
  title = {MCP-FMI: MCP Server for the Functional Mock-Up Interface},
  year = {2025},
  howpublished = {\url{https://github.com/Novia-RDI-Seafaring/mcp-fmi}},
}
```

## Acknowledgements
This work was done in the Business Finland funded project [Virtual Sea Trial](https://virtualseatrial.fi)

## License
This package is licensed under the MIT License license. See the [LICENSE](./LICENSE) file for more details.


