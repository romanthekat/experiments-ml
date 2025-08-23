Project guidelines for experiments-ml

Audience: advanced Python developer familiar with uv, LangChain/LangGraph, MCP, and local LLM runtimes (e.g., Ollama and OpenAI).

1. Build and configuration
- Runtime: Python 3.12+ (pyproject sets requires-python >=3.12). The project uses uv for environment and execution.
- Dependencies are declared in pyproject.toml. Use uv to create/refresh the environment:
  - uv sync
- Environment variables: The app relies on dotenv. Create a .env file in the project root. At minimum set:
  - NOTES_PATH=/absolute/path/to/your/markdown/notes
  - Optional/typical: any variables used by your local LLM runtime (e.g., OPENAI_API_KEY) if needed by ChatOpenAI.
- Local tools and OS constraints used by MCP tools (mcp_server.py):
  - macOS “Things” app URL scheme is invoked via open "things:///…" (add_reminder tool). Requires macOS and Things installed; otherwise these tools will error.
  - External binaries expected on PATH for notes operations:
    - get-notes-by-level (Go CLI from r-notes tooling)
    - relevant-notes (Go CLI from r-notes tooling)
    - grep, sed (used for simple_search_note); previously ag (the_silver_searcher) was used in tools_notes.py but current MCP uses grep.
  - Ensure these binaries are installed and available on PATH for the uv environment (shell PATH must be visible to uv-run subprocesses).
- LLM model: main.py uses ChatOllama with model="gpt-oss:120b" by default. You need an Ollama-compatible runtime that provides that tag or switch to a model you have locally, e.g. model="mistral-small3.2:24b-instruct-2506". Temperature is set to 1 for gpt-oss defaults.
- MCP client/server setup:
  - The app uses langchain_mcp_adapters MultiServerMCPClient.
  - Default transport configured in main.py is stdio with uv as the command and this repo as working directory:
    - "args": ["--directory", "./", "run", "mcp_server.py"], "transport": "stdio"
  - For HTTP transport, there is a commented example in main.py. If you switch to streamable_http, run the MCP server accordingly and adjust the client block.
- Running:
  - cp .env.example .env is suggested in README, but .env.example is not committed. Create .env manually as described above.
  - uv run main.py to start the interactive agent.
  - uv run mcp_server.py to run the MCP server standalone (default code path uses stdio; for HTTP, update mcp_server.py and client code accordingly).

2. Testing
- No test framework is pinned in pyproject. Use Python’s built-in unittest for simple smoke tests, or add pytest as a dev dependency if you intend to grow test coverage (not required for this project as-is).
- Running unittest with uv:
  - uv run python -m unittest -v
  - Or target a specific test file: uv run python -m unittest -v test_smoke.py
- Adding a new test (example): The following example test validates a trivial utility in main.py without hitting external dependencies.
  - Save this as test_smoke.py in the repo root:
    
    import io, sys, unittest
    from main import print_in_color
    
    class TestPrintInColor(unittest.TestCase):
        def test_print_in_color_wraps_with_ansi_blue(self):
            buf = io.StringIO()
            old_stdout = sys.stdout
            try:
                sys.stdout = buf
                print_in_color("hello")
            finally:
                sys.stdout = old_stdout
            out = buf.getvalue().rstrip("\n")
            self.assertEqual(out, "\x1b[34mhello\x1b[0m")
    
    if __name__ == "__main__":
        unittest.main(verbosity=2)
  - Run it: uv run python -m unittest -v test_smoke.py
  - Expected: 1 test passing.
  - Clean-up: Remove the test file after verification if you don’t want to keep test artifacts.
- Guidelines for adding tests:
  - Prefer isolating tests from external services. Avoid importing modules that execute network calls or spawn subprocesses on import. main.py is safe to import because its execution is guarded by if __name__ == "__main__":.
  - For MCP tool testing (mcp_server.py), mock subprocess.check_output to avoid requiring external binaries; also provide a temporary NOTES_PATH pointing to a fixture directory if you test file-related helpers.
  - If you later standardize on pytest, configure it in pyproject and consider adding ruff/black pre-commit hooks.

3. Additional development information
- Code layout overview:
  - main.py: interactive LangGraph agent connecting to MCP tools via MultiServerMCPClient; uses ChatOpenAI. The message loop streams outputs.
  - mcp_server.py: FastMCP server exposing tools for reminders and notes operations using external CLIs and filesystem access governed by NOTES_PATH.
  - helpers.py: thin wrappers for NOTES_PATH access and file IO. Note: log() writes to "~/Downloads/log.txt" with expanding ~.
  - tools_notes.py / tools_files.py: earlier LangChain tool implementations, now “Somewhat deprecated”; functionality is mirrored by MCP tools.
  - reminders.py: a simpler @tool add_reminder version using Things URL scheme; similar to MCP tool.
- Environment and platform nuances:
  - NOTES_PATH must be an absolute path to your Zettelkasten-like Markdown notes directory; filenames are addressed without .md extension (e.g., "0a context").
  - Some MCP tools read/write files directly under NOTES_PATH (e.g., save_to_notes_storage writes "0aa context generated.md"). This is a destructive overwrite by design.
  - Tags like #noai in notes trigger content redaction in read_note/read_by_zk_note_name.
  - macOS-specific behaviors: add_reminder tools require macOS with Things installed; otherwise URLs opened via open will fail.
- Debugging tips:
  - Verify that uv sees your PATH for external binaries (echo $PATH in the same shell you run uv). subprocess in MCP tools assumes these commands are available.
  - If MCP client tool discovery fails, run the server manually: uv run mcp_server.py and use the HTTP transport example (or keep stdio but confirm working directory via --directory ./ in args).
  - If ChatOpenAI fails due to missing model, switch to a model tag you have locally (model parameter in main.py) and restart.
  - For quick diagnostics of NOTES_PATH issues, add a minimal note file and use simple_search_note via MCP to validate paths.
- Style/quality:
  - No enforced formatter or linter in pyproject. If you adopt tooling: ruff, black, mypy are typical choices; keep function docstrings concise and argument names aligned with tool contracts.

4. Verified test run (for posterity)
- We verified a unittest-based smoke test (test_smoke.py as shown above) with: uv run python -m unittest -v test_smoke.py
- Result: 1 test passed. The file was subsequently removed to keep the repo clean.
