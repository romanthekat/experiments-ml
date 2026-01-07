import os
import asyncio

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel, OpenAIModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStdio, MCPServerSSE


async def build_agent() -> Agent:
    """Build a simple Pydantic-AI agent with MCP tools dynamically attached."""
    load_dotenv()

    # Model configuration (compatible with local Ollama/OpenAI-like runtimes)
    llm_model = os.getenv("LLM_MODEL", "gpt-oss:120b")
    llm_base_url = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    llm_temperature = float(os.getenv("LLM_TEMPERATURE", "1"))
    api_key = os.getenv("OPENAI_API_KEY", "sk-no-key-required-for-local")

    model = OpenAIModel(
        model_name=llm_model,
        provider=OpenAIProvider(api_key=api_key,
                                base_url=llm_base_url),
    )

    system_prompt = (
        "You are a helpful assistant to work with personal notes in zettelkasten markdown files. "
        "On a new session, refresh your memory using available tools when appropriate. "
        "Before answering, assess uncertainty; if > 0.1, ask concise clarifying questions first. "
        "Be succinct in your reasoning."
    )

    # Set up MCP client and dynamically register its tools
    mcp_server = MCPServerStdio(
        command="uv",
        args=[
            "--directory", "./", "run", "mcp_server.py",
        ],
    )

    agent = Agent(
        model=model,
        model_settings=OpenAIModelSettings(temperature=llm_temperature),
        mcp_servers=[mcp_server],
        system_prompt=system_prompt,
    )

    return agent


async def interactive_loop() -> None:
    console = Console()
    agent = await build_agent()

    # thread_id = os.getenv("AGENT_THREAD_ID", "some thread id")
    # recursion_limit = int(os.getenv("AGENT_RECURSION_LIMIT", "42"))
    console.print(Panel("[blue]pydantic-ai agent ready"))

    message_history = []
    while True:
        try:
            user_message = input(">> ").strip()
        except EOFError:
            break
        if not user_message.strip():
            continue

        console.print(Panel(f"[green]{user_message}", title="Input", title_align="left"))

        try:
            result = await agent.run(user_message,
                                     message_history=message_history,)
            message_history = result.all_messages()
            console.print(Panel(str(result.output), title="Assistant", title_align="left"))
        except Exception as e:
            console.print(Panel(f"Error: {e}", title="Assistant", title_align="left"))


if __name__ == "__main__":
    asyncio.run(interactive_loop())
