# experiments-ml

LangGraph-based agent wired to an MCP server for working with a local Zettelkasten notes corpus and reminders (Things.app).  
Uses uv for environment, dotenv for config, and a local OpenAI/Ollama-compatible runtime by default.

## Requirements
- Python 3.12+
- uv installed (https://docs.astral.sh/uv/)
- External tools on PATH for notes operations:
  - get-notes-by-level (from https://github.com/romanthekat/r-notes)
  - relevant-notes (from the same repo)
  - grep, sed
- macOS + Things app installed for reminders (optional; required for add_reminder)
- Local LLM runtime exposing an OpenAI-compatible API (default base_url http://localhost:1234/v1)

## Setup
1. Sync deps
   - `uv sync`
2. Configure environment
   - `cp .env.example .env` and set at minimum:
     - NOTES_PATH=/absolute/path/to/your/markdown/notes
   - Optional/typical:
     - OPENAI_API_KEY (if your runtime checks it)
     - LLM_MODEL (default: openai/gpt-oss-120b)
     - LLM_BASE_URL (default: http://localhost:1234/v1)
     - LLM_TEMPERATURE (default: 1)
     - AGENT_RECURSION_LIMIT (default: 42)
     - AGENT_THREAD_ID (default: some thread id)

## Running
- Start the interactive agent:
  - `uv run main.py`
- MCP transport defaults to stdio, spawning the server via `uv run mcp_server.py` under the hood.
  - To experiment with HTTP, see commented example in main.py and run: uv run mcp_server.py

## Notes
- NOTES_PATH must be an absolute, existing directory. The server will raise a clear error if misconfigured.
- Ensure your shell PATH (where the external CLIs live) is visible to processes launched via uv.

## Tests (optional)
- A trivial smoke test can be run without external services:
  - uv run python -m unittest -v test_smoke.py