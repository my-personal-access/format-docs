"""Checks module."""
from src import files
from src import folders
from os import rename, chdir, getcwd, remove as osremove
from os.path import exists, abspath
from jinja2 import Template
import src.constants as cst 
from src.override import move, mkdir, rmdir, remove
from src import lot
from src.yaml import LotDumper
import yaml
import copy
from deepdiff import DeepDiff
from re import search, findall
from src.markdown import altair_to_urssaf

def create_important_folders():
    """Check if important folder are created."""
    folders_ = folders.get_all()
    for path in map(lambda b: b['path'], filter(lambda a: a['is_file'] is False and a['path'] not in folders_, cst.all__())):
        mkdir(path)


def check_missing_trains():
    """Check missing train folders & create missing ones."""
    flat_files_train = list(set([files.get_train(f) for f in files.get_lots()]))
    for flat_file_train in flat_files_train:
        if flat_file_train not in list(map(lambda el: el.split('/')[-1], folders.get_trains())):
            mkdir(cst.lots() + '/' + flat_file_train)


def scan_files_references(moved_lots_ref: dict[str, str]):
    """Scan all files and make references between files."""
    root = getcwd()
    files_references = {}
    for lot__ in files.get_lots():
        errno, _, md = lot.try_open_yml(lot__)
        file_inclusion_regex = r"!?\[.*\]\([A-Za-z0-9\.\/\_\- ]+\)"
        if errno == 0 and search(file_inclusion_regex, md):
            refs = []
            file_path_regex = r"\([A-Za-z0-9\.\/\_\- ]+\)"
            for ref in findall(file_inclusion_regex, md):
                file_ref_rel = search(file_path_regex, ref).group(0)[1:-1]
                chdir('/'.join((lot__ if lot__ not in moved_lots_ref.keys() else moved_lots_ref[lot__]).split('/')[:-1]))
                if exists(file_ref_rel):
                    full_rel_path = cst.project + abspath(file_ref_rel).replace('\\', '/').split(cst.project)[-1]
                    refs.append({'rel': file_ref_rel, 'abs': full_rel_path})
                chdir(root)
            if len(refs) > 0: files_references[lot__] = refs

    return files_references


def move_referenced_files(ref_files: dict[str, list[dict[str, str]]]):
    """Move referenced files from scanned files."""
    changed_paths = {}
    for file_key, refs in ref_files.items():
        for ref_index, ref in enumerate(refs):
            abs = ref['abs']
            dest = 'images' if files.is_image(abs) else 'fichiers'
            
            if exists(abs):
                train_file_key = files.is_in_train_folder(file_key)
                __fol = eval('cst.' + dest)(train_file_key if train_file_key is not None else cst.orphans)
                entity_filename = files.get_filename(abs)
                if not exists(__fol):
                    mkdir(__fol)
                dest_entity_filename = __fol + '/' + entity_filename
                if abs != dest_entity_filename:
                    move(abs, dest_entity_filename)
                new_relative_path = f'../../{dest}/{folders.get_last_folder(__fol)}/{entity_filename}'
                ref_files[file_key][ref_index] = { **ref, 'update_rel': new_relative_path}
                changed_paths[abs] = new_relative_path
            else:
                ref_files[file_key][ref_index] = { **ref, 'update_rel': changed_paths[abs]}
    return ref_files                            


def move_orphans():
    """Move orphan files that get no references in files."""
    for orphan in files.get_not_md():
        filename = files.get_filename(orphan)
        dest = cst.images(cst.orphans) + f'/{filename}' if files.is_image(orphan) else cst.fichiers(cst.orphans) + f'/{filename}'
        if orphan != dest:
            move(orphan, dest)


def change_fichiers_images_path(ref_files: dict[str, list[dict[str, str]]]):
    """Change images and fichiers relative directory path."""
    for lot__, refs in ref_files.items():
        lot.change_fichiers_images_path_v2(lot__, refs)


def move_lots():
    """Move lots to train folder."""
    ref_moved = {}
    for l__ in files.get_lots():
        train = files.get_train(l__)
        train_folder = cst.lots() + '/' + train
        if '/'.join(l__.split('/')[:-1]) != train_folder:
            try:
                move(l__, train_folder)
                ref_moved[train_folder + '/' + files.get_filename(l__)] = l__
            except Exception:
                cst.review_log.error(f"Could not move '{l__}' to '{train_folder}'")
    return ref_moved


def move_files():
    """Move lots & attachment files."""
    moved_lots = move_lots()
    ref_files = scan_files_references(moved_lots)
    updated_ref_files = move_referenced_files(ref_files)
    move_orphans()
    change_fichiers_images_path(updated_ref_files)


def check_lots_name():
    """Check MERGED tag in lot name."""
    for folder in folders.get(cst.lots()):
        local_lots = files.get(folder)
        local_lots.sort()

        initial_lot = local_lots[0]
        if cst.merged_tag in initial_lot.upper():
            rename(initial_lot, initial_lot.replace('_' + cst.merged_tag, ''))
        
        for not_initial_lot in local_lots[1:]:
            if cst.merged_tag not in not_initial_lot.upper():
                ext = files.get_ext(not_initial_lot)
                path = files.get_path(not_initial_lot)
                new_filename = path + '/' + (files.get_filename(not_initial_lot).replace('.' + ext, '') + "_" + cst.merged_tag) + "." + ext
                rename(not_initial_lot, new_filename)


def check_common_errors():
    """Check common errors."""
    for file in files.get_lots():
        lot.common_errors(file)


def remove_empty_trains():
    """Remove empty train folders."""
    for train in folders.get_trains():
        __f = files.get__(train)
        if len(__f) == 0:
            rmdir(train)
        else:
            for file in __f:
                if files.get_filename(file) == '.gitkeep':
                    remove(file)
            __f__ = files.get__(train)
            if len(__f__) == 0:
                rmdir(train)

def check_parsing_yml():
    """Try to parse all lot into yml file."""
    for file in files.get_lots():
        errno, data_yml, _ = lot.try_open_yml(file)
        if errno > 0:
            fn = files.get_filename(file)
            if data_yml != "":
                err_msg = f"Category: Parsing YAML | File '{fn}'"\
                + str("\t\t\t" if cst.merged_tag not in fn else '\t')\
                + f"unparsable to YML format | Cause: {data_yml}"
                cst.review_log.warning(msg = err_msg)


def no_regression_one_file(file: str):
    """Check all keys in one file only."""
    errno, data_yml, md = lot.try_open_yml(file)
    if errno == 0:
        data_yml_ = lot.check_main_keys(files.get_filename(file), copy.deepcopy(data_yml))
        md_ = altair_to_urssaf(md)

        if DeepDiff(data_yml, data_yml_, ignore_order=True) or DeepDiff(md, md_, ignore_order=True):
            with open(file, 'w', encoding=cst.encoding) as f__:
                f__.write(lot.build_lot(yml=yaml.dump(data_yml_, sort_keys=False, Dumper=LotDumper,\
                    allow_unicode=True, width=float("inf")), md=md_))

def check_no_regression():
    """Check no regression on all trains."""
    trains = folders.get_trains()
    for train in trains:
        lots = files.get(train)
        lots.sort()
        len__ = len(lots)
        for i_lots in range(len__):
            if i_lots == 0:
                no_regression_one_file(lots[0])
            if i_lots + 1 < len__:
                lot.no_regression(lots[i_lots], lots[i_lots + 1])
            else:
                no_regression_one_file(lots[i_lots])
                

def create_important_files():
    """Check if important files are created."""
    for el in filter(lambda a: a['is_file'] is True, cst.all__()):
        
        path = el['path']
        
        if exists(path): osremove(path)
        
        filename = path.split('/')[-1]
        with open(f'src/templates/{filename}.j2', 'r', encoding=cst.encoding) as f:
            template = Template(f.read())
            
            with open(path, 'w', encoding=cst.encoding) as n:
                if el['data'] is not None:
                    render = template.render(el['data'])
                else:
                    render = template.render()
                n.write(render)


def delete_gitkeeps():
    """Delete all .gitkeep files."""
    gitkeeps = files.get_gitkeeps()
    for gitkeep in gitkeeps:
        remove(gitkeep)