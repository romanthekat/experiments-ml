import os
import asyncio
from typing import List, Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel, OpenAIModelSettings
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStdio

# --- Configuration & Model Setup ---

def get_model() -> OpenAIModel:
    """Helper to initialize the model based on environment variables."""
    load_dotenv()
    llm_model = os.getenv("LLM_MODEL", "gpt-oss:120b")
    llm_base_url = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
    api_key = os.getenv("OPENAI_API_KEY", "sk-no-key-required-for-local")
    
    return OpenAIModel(
        model_name=llm_model,
        provider=OpenAIProvider(api_key=api_key, base_url=llm_base_url),
    )

def get_model_settings() -> OpenAIModelSettings:
    llm_temperature = float(os.getenv("LLM_TEMPERATURE", "1"))
    return OpenAIModelSettings(temperature=llm_temperature)

# --- MCP Setup (For knowledge access by the Analyst) ---
mcp_server = MCPServerStdio(
    command="uv",
    args=["--directory", "./", "run", "mcp_server.py"],
)

# --- Expert 1: The Analyst ---
# Focuses on facts, data, and using tools to find information.
analyst_agent = Agent(
    model=get_model(),
    model_settings=get_model_settings(),
    mcp_servers=[mcp_server],
    system_prompt=(
        "You are the Analyst. Your role is to provide factual, data-driven insights. "
        "Use your tools to search through notes if needed. Focus on 'what' and 'how'. "
        "Be precise, objective, and highlight key facts."
    ),
)

# --- Expert 2: The Strategist ---
# Focuses on high-level goals, "why", and broader implications.
strategist_agent = Agent(
    model=get_model(),
    model_settings=get_model_settings(),
    system_prompt=(
        "You are the Strategist. Your role is to look at the big picture and long-term goals. "
        "Focus on 'why' and the overall value. Think about connections between different ideas "
        "and how they fit into a larger strategy."
    ),
)

# --- Expert 3: The Critic ---
# Focuses on risks, flaws, edge cases, and skepticism.
critic_agent = Agent(
    model=get_model(),
    model_settings=get_model_settings(),
    system_prompt=(
        "You are the Critic. Your role is to find potential flaws, risks, or edge cases "
        "in the proposed solutions or ideas. Be skeptical but constructive. "
        "What are we missing? What could go wrong? What are the hidden assumptions?"
    ),
)

# --- Orchestrator: The Facilitator ---
# Manages the discussion and synthesizes the final answer.
orchestrator_agent = Agent(
    model=get_model(),
    model_settings=get_model_settings(),
    system_prompt=(
        "You are the Facilitator of a 'Mixture of Experts' discussion. "
        "Your goal is to provide a comprehensive answer by consulting three experts: "
        "an Analyst, a Strategist, and a Critic. "
        "\n"
        "Process: "
        "1. Identify the core components of the user's question. "
        "2. Consult each expert using their respective tools to get their unique perspective. "
        "3. Synthesize a final, balanced response that incorporates the best insights from all three. "
        "4. Address any conflicts or trade-offs identified by the experts. "
        "5. Be clear about what is a fact (Analyst), a strategy (Strategist), or a risk (Critic)."
    ),
)

@orchestrator_agent.tool
async def consult_analyst(ctx: RunContext[None], query: str) -> str:
    """Consult the Analyst for factual data and technical details."""
    print(f"  [Facilitator -> Analyst] Analyzing: '{query}'...")
    result = await analyst_agent.run(query)
    return result.output

@orchestrator_agent.tool
async def consult_strategist(ctx: RunContext[None], query: str) -> str:
    """Consult the Strategist for high-level goals and strategic value."""
    print(f"  [Facilitator -> Strategist] Thinking strategically about: '{query}'...")
    result = await strategist_agent.run(query)
    return result.output

@orchestrator_agent.tool
async def consult_critic(ctx: RunContext[None], query: str) -> str:
    """Consult the Critic to identify risks, flaws, or missing pieces."""
    print(f"  [Facilitator -> Critic] Reviewing risks for: '{query}'...")
    result = await critic_agent.run(query)
    return result.output

# --- Interactive Loop ---
async def interactive_loop() -> None:
    console = Console()
    console.print(Panel("[bold green]Pydantic-AI Mixture of Experts (MoE) Agent Ready"))
    console.print("Experts: [blue]Analyst[/blue], [magenta]Strategist[/magenta], [red]Critic[/red]\n")

    message_history = []
    while True:
        try:
            user_message = input(">> ").strip()
        except EOFError:
            break
        if not user_message:
            continue
        if user_message.lower() in ("exit", "quit"):
            break

        console.print(Panel(f"[green]{user_message}", title="User Input", title_align="left"))

        try:
            # The orchestrator handles the request and calls sub-agents as needed
            result = await orchestrator_agent.run(
                user_message,
                message_history=message_history,
            )
            message_history = result.all_messages()
            
            console.print(Panel(str(result.output), title="MoE Synthesized Response", title_align="left"))
        except Exception as e:
            console.print(Panel(f"Error: {e}", title="System Error", title_align="left", border_style="red"))

if __name__ == "__main__":
    asyncio.run(interactive_loop())
