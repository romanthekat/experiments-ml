import subprocess
from urllib.parse import quote

from langchain_core.tools import tool


@tool
def add_reminder(title: str, notes: str) -> str:
    """
    Adds a reminder for the human operator, using simple text inputs only.
    This tool supports alphanumeric, spaces, and brackets in 'title' and 'notes' - DO NOT USE OTHER SPECIAL SYMBOLS.
    Slashes, ampersands, quotes are not supported!

    :param title: reminder title **without special symbols or punctuation**. for example: check [[0 inbox]]
    :param notes: reminder notes **without special symbols or punctuation**
    :return: command execution output
    """
    safe_title = quote(title, safe='')
    safe_notes = quote(notes, safe='')
    cmd = f'open "things:///add?title={safe_title}&notes={safe_notes}&tags=agent"'
    return subprocess.check_output(cmd, shell=True, text=True)


# @tool
def get_reminders_for_today() -> str:
    """
    Returns all reminders for today.
    :return: list of reminders for today"
    """
    url_to_get_reminders = "things:///show?id=today"
    return subprocess.check_output(url_to_get_reminders, shell=True, text=True)
