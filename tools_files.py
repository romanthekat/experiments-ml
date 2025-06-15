from langchain_core.tools import tool

# Somewhat deprecated, see mcp_server.py instead

@tool
def read_permanent_agent_memory():
    """
    Returns permanent memory of the agent, which can be shared between runs.
    Use it whenever you see something important in the permanent memory, that can be handy for you in the next runs.
    To be used in combination with write_permanent_memory. Use as often as you see fit.
    ALWAYS READ IT IN THE BEGINNING OF YOUR RUNS.
    :return: permanent memory as string
    """
    with open("permanent_memory.txt", "r") as file:
        return file.read()


@tool
def write_permanent_agent_memory(text: str):
    """
    Writes permanent memory for the LLM/AI agent, which can be shared between runs.
    To be used in combination with read_permanent_memory. Use as often as you see fit.
    :param text: text to write, OVERRIDING original data.
    :return: None
    """
    with open("permanent_memory.txt", "w") as file:
        file.write(text)
