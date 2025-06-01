import subprocess

from langchain_core.tools import tool


# things:///add?
#     title=Buy%20milk&
#     notes=High%20fat

@tool
def add_reminder(title: str, notes: str) -> str:
    """
    Adds a reminder for the human operator, using simple text inputs only.
    This tool supports alphanumeric, spaces, and brackets in 'title' and 'notes' - DO NOT USE SPECIAL SYMBOLS.
    Slashes and ampersands are not supported!

    :param title: reminder title **without special symbols or punctuation**
    :param notes: reminder notes **without special symbols or punctuation**
    :return: command execution output
    """
    url_to_add_note = f"open 'things:///add?title={title}&notes={notes}&tags=agent'"
    return subprocess.check_output(url_to_add_note, shell=True, text=True)


# @tool
def get_reminders_for_today() -> str:
    """
    Returns all reminders for today, in wikilink format.
    :return: list of reminders for today, in wikilink format, f.e. "[[0aa context]]"
    """
    url_to_get_reminders = "things:///show?id=today"
    return subprocess.check_output(url_to_get_reminders, shell=True, text=True)