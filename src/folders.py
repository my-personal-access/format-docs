"""Check folder name rules."""
from os import listdir, path
import src.constants as cst

def get(path_):
    """Get folders in current path."""
    return [path_ + '/' + entity for entity in listdir(path_) if path.isdir(path_ + '/' + entity)]

def get_all(directory = None, folders = []):
    """Get all folders recursively."""
    if directory is None: directory = cst.project
    sub = get(directory)
    folders.extend(sub)
    for folder in sub:
        get_all(folder, folders)
    return folders


def get_trains():
    """Get train folders in /lots."""
    return get(cst.lots())


def get_last_folder(path: str):
    """Get last folder from long path."""
    return str(path.split('/')[-1])