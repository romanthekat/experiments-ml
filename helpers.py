import os


def _get_notes_folder_path():
    path = os.getenv("NOTES_PATH")
    if not path:
        raise ValueError("NOTES_PATH is not set. Create a .env with NOTES_PATH=/absolute/path/to/your/markdown/notes")
    if not os.path.isabs(path):
        raise ValueError(f"NOTES_PATH must be an absolute path, got: {path}")
    if not os.path.isdir(path):
        raise ValueError(f"NOTES_PATH does not point to an existing directory: {path}")
    return path


def _get_note_path(note_name: str):
    return f"{_get_notes_folder_path()}/{note_name}.md"


def _read_text_file(file_path: str) -> str:
    with open(file_path, "r") as file:
        return file.read()


def log(entry: str):
    with open(os.path.expanduser("~/Downloads/log.txt"), "a") as file:
        file.write(entry)
        file.write("\n")
