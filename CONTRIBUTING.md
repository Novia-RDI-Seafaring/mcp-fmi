# Contributing to MCP-FMU

Thank you for your interest in contributing to MCP-FMU! This document provides guidelines and instructions for development.

## Development Setup

### Prerequisites
- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/pip/packages/) package manager
- Git

### Local Setup
1. Fork and clone the repository
2. Create and activate a virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install development dependencies:
   ```bash
   uv pip install -e ".[dev]"
   ```

### Running the Server
Run the server and the MCP Inspector:
```bash
# With default FMU directory (static/fmus)
uv run --with mcp --with mcp-fmi --with python-dotenv --with fmpy --with numpy --with pydantic mcp dev src/mcp_fmi/server.py

# With custom FMU directory
uv run --with mcp --with mcp-fmi --with python-dotenv --with fmpy --with numpy --with pydantic mcp dev src/mcp_fmi/server.py /path/to/fmu/folder
```

## Development Workflow

### Version Management
This project uses `hatch` for version management. To work with versions:

```bash
# View current version
hatch version

# Bump version
hatch version patch  # 0.0.1 -> 0.0.2
hatch version minor  # 0.0.1 -> 0.1.0
hatch version major  # 0.0.1 -> 1.0.0
```

### Making Changes
1. Create a new branch for your changes
2. Make your changes
3. Run tests: `pytest`
4. Commit your changes with clear commit messages
5. Push your branch and create a pull request

### Releasing a New Version
1. Ensure all tests pass: `pytest`
2. Bump version and commit changes:
   ```bash
   hatch version patch  # or minor/major
   git add -p
   git commit -m "Bump version to $(hatch version)"
   ```
3. Create and push the tag:
   ```bash
   git tag v$(hatch version)
   git push --tags
   ```
4. GitHub Actions will automatically:
   - Build the package using `uv build`
   - Run tests
   - Publish to PyPI

## Automated Release Process
The project uses GitHub Actions to automatically publish to PyPI when you push a new version tag. The workflow:
- Triggers on tags matching `v*` (e.g., `v0.1.0`)
- Installs dependencies using `uv`
- Runs tests
- Builds the package using `uv build`
- Publishes to PyPI

You can monitor the release process in the "Actions" tab of your GitHub repository.

## Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions and classes
- Add tests for new features

## Testing
Run tests with:
```bash
pytest
```

## Questions?
Feel free to open an issue if you have any questions about contributing! 