"""Manage files."""
from os import path, listdir
import src.constants as cst
from glob import glob
from re import match

def get(directory: str):
    """Get all files except hidden one in current directory."""
    return [directory + '/' + entity for entity in listdir(directory) if not path.isdir(directory + '/' + entity) and entity[0] != '.']


def get__(directory: str):
    """Get all files in current directory."""
    return [directory + '/' + entity for entity in listdir(directory) if not path.isdir(directory + '/' + entity)]


def get_all():
    """Get all files recursively from root."""
    return list(map(lambda b: b.replace('\\', '/'), filter(path.isfile, glob(cst.project + '/**/*', recursive=True))))


def get_gitkeeps():
    """Get all .gitkeep files."""
    return list(filter(lambda el: el.split('/')[-1] == ".gitkeep", \
        map(lambda b: b.replace('\\', '/'), glob(cst.project + '/**/.*', recursive=True))))


def get_filename(file: str):
    """Extract filename from path."""
    return file.split('/')[-1]


def get_ext(file: str):
    """Get file extension."""
    return file.split('/')[-1].split('.')[-1]


def get_path(file: str):
    """Get file path without filename."""
    return '/'.join(file.split('/')[:-1])


def is_image(file: str):
    """Check if file is image."""
    return get_ext(file).lower() in cst.pictures_ext


def is_fichier(file: str):
    """Check if file is fichier."""
    ext = get_ext(file).lower()
    return ext not in cst.pictures_ext and ext != cst.markdown_ext


def get_docs_files():
    """Returns all files in /project/docs folder."""
    # Get all files in /docs
    return list(filter(lambda el: cst.docs() + '/' in el, get_all()))


def get_lots_files():
    """Returns all files in /project/docs/lots folder."""
    # Get all files in /docs/lots
    return list(filter(lambda el: cst.lots() + '/' in el, get_all()))


def get_not_md():
    """Get all files that are neither markdown nor hidden ones."""
    # Remove markdown files
    # fichiers = list(filter(lambda el: cst.markdown_ext != get_ext(el), get_docs_files()))
    fichiers = list(filter(lambda el: cst.markdown_ext != get_ext(el), get_lots_files()))
    # Remove hidden files
    fichiers = list(filter(lambda el: '.' not in str(el).split('/')[-1][0], fichiers))
    return fichiers


def get_fichiers():
    """Get fichiers files from root."""
    return list(filter(is_fichier, get_not_md()))


def get_images():
    """Get images files from root."""
    return list(filter(is_image, get_not_md()))


def get_md():
    """Get mardown files."""
    return list(filter(lambda el: cst.markdown_ext == get_ext(el), get_docs_files()))


def get_lots():
    """Get all lots in /lots."""
    return list(filter(lambda f: cst.lots() in f, get_md()))


def get_train(file: str, long_train: bool = False):
    """Get train from file path."""
    full = get_filename(file)[:6]
    return full if full[4:] != '00' else (full[:4] + ("00" if long_train is True else ''))


def convert_lots_to_json(lots: list = []):
    """Groups lots by train."""
    json = {}
    if lots == []: lots = get_lots()
    for lot in lots:
        train = get_train(lot, True)
        if train not in json.keys(): json[train] = []
        json[train].append(lot.replace(cst.docs(), '')[1:])
    return json


def is_in_train_folder(file: str):
    """Check if subfolder's file is train or not."""
    subfolder = file.split('/')[:-1][-1]
    if match(r"^(\d{4}|\d{6})$", subfolder):
        return subfolder
    return None