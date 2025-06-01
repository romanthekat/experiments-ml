import subprocess

from langchain_core.tools import tool


# things:///add?
#     title=Buy%20milk&
#     notes=High%20fat

@tool
def add_reminder(title: str, notes: str) -> str:
    """
    Adds a reminder for the human operator. DO NOT USE SPECIAL SYMBOLS IN TITLE OR NOTES as it gets glitchy.
    :param title: reminder title
    :param notes: reminder notes
    :return: command execution output
    """
    url_to_add_note = f"open 'things:///add?title={title}&notes={notes}&tags=agent'"
    return subprocess.check_output(url_to_add_note, shell=True, text=True)
