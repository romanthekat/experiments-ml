# experiments-ml

Currently, contains experiment with langchain/personal agent and custom tools for working with my notes.    
Agent can access notes, has simple permanent memory, access to a single note file in my notes storage, has a bunch of wrappers for [r-notes](https://github.com/romanthekat/r-notes) as well as a few custom tools, and can create reminders.

## Usage
`cp .env_template .env`  
`uv sync`  

`uv run mcp_server.py`  
`uv run main.py`  