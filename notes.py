import os

from langchain_core.tools import tool


def _read_text_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


@tool
def read_by_note_name(note_name: str) -> str:
    """
    Returns note content by given note full name. e.g. "0a context" or "14.2 deutsch language".
    Note name must always be full, as mentioned in [[wikilinks]] entries.
    So that a link [[14.2 deutsch language]] means filename is '14.2 deutsch language'.

    :param note_name: full note name, e.g. "0a context" or "14.2 deutsch language"
    :return: note content as string
    """
    file_path = f"{os.getenv("NOTES")}/{note_name}.md"
    print(file_path)
    return _read_text_file(file_path)


@tool
def read_core_context_note():
    """
    returns the core context note content
    :return:
    """
    return read_by_note_name.invoke("0a context")
