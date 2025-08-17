import os


def _get_notes_folder_path():
    return os.getenv("NOTES_PATH")


def _get_note_path(note_name: str):
    return f"{_get_notes_folder_path()}/{note_name}.md"


def _read_text_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


def log(entry: str):
    with open("~/Downloads/log.txt", "a") as file:
        file.write(entry)
        file.write("\n")
