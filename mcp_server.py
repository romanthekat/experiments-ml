import os
import shlex
import subprocess
from json.encoder import encode_basestring_ascii
from urllib.parse import quote

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from helpers import _get_notes_folder_path, _get_note_path, _read_text_file

mcp = FastMCP("r-notes")


@mcp.tool()
def add_reminder(title: str, notes: str, when: str = "") -> str:
    """
    Adds a reminder for the human operator, using simple text inputs only.
    This tool supports alphanumeric, spaces, and brackets in 'title' and 'notes' - DO NOT USE OTHER SPECIAL SYMBOLS.
    Slashes, ampersands, quotes are not supported!

    :param title: reminder title **without special symbols or punctuation**. for example: check [[0 inbox]]
    :param notes: reminder notes **without special symbols or punctuation**
    :param when: optional parameter with the following possible values: today, tomorrow, evening, anytime, someday, a date string, or a date time string
    :return: command execution output
    """
    safe_title = quote(title, safe='')
    safe_notes = quote(notes, safe='')
    safe_when = quote(when, safe='')
    cmd = f'open "things:///add?title={safe_title}&notes={safe_notes}&tags=agent&when={safe_when}"'
    return subprocess.check_output(cmd, shell=True, text=True)


@mcp.tool()
def read_main_context():
    """
    Reads and returns two main context notes, joining the content of both: 'context note' and 'personal index note'.
    'Context note' is an important note, which refers to things that are actual 'at the moment overall'.
    'Personal index note' is a special note, which refers to things many 'important' notes.

    Use this tool to get a bird's eye view on a notes collection, a good entry point to look things up.

    :return: 'context note' + 'personal index note' content as string
    """
    context_note = read_note("0a context")
    personal_note = read_note("10 Σ personal index")

    return context_note + "\n" + personal_note


# Permanent memory
@mcp.tool()
def read_permanent_agent_memory():
    """
    Returns permanent memory of the agent, which can be shared between runs.
    Use it whenever you see something important in the permanent memory, that can be handy for you in the next runs.
    To be used in combination with write_permanent_memory. Use as often as you see fit.

    ALWAYS READ IT AT THE BEGINNING OF YOUR RUNS.

    :return: permanent memory as string
    """
    with open("permanent_memory.txt", "r") as file:
        return file.read()


@mcp.tool()
def write_permanent_agent_memory(text: str):
    """
    Writes permanent memory for the LLM/AI agent, which can be shared between runs.
    To be used in combination with read_permanent_memory. Use as often as you see fit.

    :param text: text to write, OVERRIDING original data.
    :return: None
    """
    with open("permanent_memory.txt", "w") as file:
        file.write(text)


# Lower level notes tools
@mcp.tool()
def get_notes_by_level(level: int = 1) -> str:
    """
    Returns subset of notes, limited by top notes by given level. Level generally doesn't exceed 4-5.

    Use this tool to get a very high-level overview of which notes are there in the collection.

    :param level: positive number, level of notes to return, f.e. 1 for top level notes, 2 for top level notes of level 1 and level 2, etc.
    :return: list of zk note names in wikilinks format, f.e. "[[0a context]]" or "[[11 blog]]"
    """
    folder_to_search_in = _get_notes_folder_path()
    notes_path = shlex.quote(folder_to_search_in)
    command = f"get-notes-by-level -notesPath={notes_path} -level={level}"
    return subprocess.check_output(command, shell=True, text=True)


@mcp.tool()
def simple_search_note(text: str) -> str:
    """
    Executes a simple search in notes by a given text.

    :param text: a text to search by
    :return: list of zk note names or empty string if nothing is found, f.e. "0a context" or "14.2 deutsch language"
    """
    folder_to_search_in = _get_notes_folder_path()
    # command = f'ag "{text}" --nocolor --nopager -l -i "{folder_to_search_in}" | sed "s=.*/=="' # stopped working from subprocess, successfully returns nothing
    # command = f'grep "{text}" -Rl "{folder_to_search_in}" | sort -n | sed "s=.*/=="'
    # command = f'find "{folder_to_search_in}" -iname "*{text}*.md" | sort -n | sed "s=.*/=="'
    safe_text = shlex.quote(text)
    safe_path = shlex.quote(folder_to_search_in)
    command = f"grep -Rl {safe_text} {safe_path} | sed 's=.*/=='"
    output = subprocess.check_output(command, shell=True, text=True)
    return output.replace(".md", "")


@mcp.tool()
def find_relevant_notes(zk_note_name: str) -> str:
    """
    Returns notes which are relevant to a given note, in wikilink format.

    Use when you need to find which other notes are related to a given note.

    :param zk_note_name: full note name in zettelkasten format, f.e. "0a context" or "14.2 deutsch language". NEVER include .md extension.
    :return:
    """
    note_path = shlex.quote(_get_note_path(zk_note_name))
    command = f"relevant-notes -notePath={note_path}"
    return subprocess.check_output(command, shell=True, text=True)


# unstable, output is too huge, so it gets truncated
# @mcp.tool()
def read_note_and_subtree(zk_note_name: str) -> str:
    """
    Reads note content and all notes in the same notes tree, by given note zk full name.

    Use only if you need to load of related context for the given note, as it will return a huge number of tokens.

    :param zk_note_name: full note name in zettelkasten format, f.e. "0a context" or "14.2 deutsch language". NEVER include .md extension.
    :return: content of the requested note and all notes down in the same tree
    """
    command = f"rank-join -notesPath='{_get_notes_folder_path()}' -filterMainNote='{zk_note_name}'"
    return subprocess.check_output(command, shell=True, text=True)


@mcp.tool()
def read_note(zk_note_name: str) -> str:
    """
    Returns note content by given note zk full name. f.e. "0a context" or "14.2 deutsch language".
    Note name must always be full, as mentioned in [[wikilinks]] entries.
    So that a link [[14.2 deutsch language]] means filename is '14.2 deutsch language'.

    Use this tool to read a note content.

    :param zk_note_name: full note name in zettelkasten format, e.g. "0a context" or "14.2 deutsch language"
    :return: note content as string
    """
    file_path = _get_note_path(zk_note_name)
    note_content = _read_text_file(file_path)

    if "#noai" in note_content:
        return "this note content can't be accessed due to #noai tag."

    return note_content


@mcp.tool()
def save_to_notes_storage(text: str):
    """
    Saves text to notes storage for human operator. Uses a Markdown format.
    Use when you need to save information to the notes' storage, when asked to 'save it for me' and similar requests.
    Use #tags if you see it useful, add them at the beginning of the text.
    :param text: text to write, overriding the note
    """
    note_path = f"{_get_notes_folder_path()}/0aa context generated.md"
    with open(note_path, "w") as file:
        header = """# 0aa context generated #index #flag #ai\n"""
        file.write(header + text)


if __name__ == "__main__":
    load_dotenv()

    # Initialize and run the server
    # mcp.run(transport='streamable-http')
    mcp.run(transport='stdio')

## not supported in practice -> skip
# @mcp.resource("echo://{message}")
# def echo_resource(message: str) -> str:
#     """Echo a message as a resource"""
#     return f"Resource echo: {message}"

## not supported in practice -> skip
# @mcp.prompt()
# def echo_prompt(message: str) -> str:
#     """Create an echo prompt"""
#     return f"Please process this message: {message}"
