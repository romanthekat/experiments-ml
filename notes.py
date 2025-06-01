import os
import subprocess

from langchain_core.tools import tool

# TODO create custom MCP server out of this below instead (?)

@tool
def get_notes_by_level(level: int = 1) -> str:
    """
    Returns subset of notes, limited by top notes by given level. Level generally doesn't exceed 4-5.
    :param level: positive number, level of notes to return, f.e. 1 for top level notes, 2 for top level notes of level 1 and level 2, etc.
    :return: list of zk note names in wikilinks format, f.e. "[[0a context]]" or "[[11 blog]]"
    """
    folder_to_search_in = _get_notes_folder_path()
    command = f"get-notes-by-level -notesPath='{folder_to_search_in}' -level={level}"
    return subprocess.check_output(command, shell=True, text=True)


@tool
def simple_search_note(text: str) -> str:
    """
    Executes simple search in notes by a given text.
    :param text: a text to search by
    :return: list of zk note names or empty string if nothing found, f.e. "0a context" or "14.2 deutsch language"
    """
    folder_to_search_in = _get_notes_folder_path()
    command = f'ag "{text}" -l -i "{folder_to_search_in}" | sed "s=.*/=="'
    output = subprocess.check_output(command, shell=True, text=True)
    return output.replace(".md", "")


@tool
def find_relevant_notes_by_zk_note_name(zk_note_name: str) -> str:
    """
    Returns notes which are relevant to a given note, in wikilink format.
    :param zk_note_name: full note name in zettelkasten format, f.e. "0a context" or "14.2 deutsch language". IT NEVER includes .md extension.
    :return:
    """
    command = f"relevant-notes -notePath='{_get_note_path(zk_note_name)}'"
    return subprocess.check_output(command, shell=True, text=True)


@tool
def read_by_zk_note_name(zk_note_name: str) -> str:
    """
    Returns note content by given note zk full name. f.e. "0a context" or "14.2 deutsch language".
    Note name must always be full, as mentioned in [[wikilinks]] entries.
    So that a link [[14.2 deutsch language]] means filename is '14.2 deutsch language'.

    :param zk_note_name: full note name in zettelkasten format, e.g. "0a context" or "14.2 deutsch language"
    :return: note content as string
    """
    file_path = _get_note_path(zk_note_name)
    return _read_text_file(file_path)


@tool
def read_context_note():
    """
    Returns 'context note' content.
    'Context note' is an important note, refers to things that are actual 'at the moment overall'.
    :return: 'context' note content as string
    """
    return read_by_zk_note_name.invoke("0a context")


def _get_notes_folder_path():
    return os.getenv("NOTES")


def _get_note_path(note_name: str):
    return f"{_get_notes_folder_path()}/{note_name}.md"


def _read_text_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()
