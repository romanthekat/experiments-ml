from langchain_core.tools import tool
from notes import _get_notes_folder_path


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


@tool
def save_to_notes_storage(text: str):
    """
    Saves text to notes storage for human operator. Uses a Markdown format.
    Use when you need to save information to the notes' storage, when asked to 'save it for me' and similar requests.
    Use #tags if you see it useful, add them in the beginning of the text.
    :param text: text to write, overriding the note
    """
    note_path = f"{_get_notes_folder_path()}/0aa context generated.md"
    with open(note_path, "w") as file:
        header = """# 0aa context generated
#index #flag

"""
        file.write(header + text)
