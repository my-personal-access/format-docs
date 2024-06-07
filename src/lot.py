"""Module operate on lot files."""
from re import search, sub, findall
from src import constants as cst
from numpy import array_equal
from src.files import get_filename, is_image
from src import folders
import yaml
from yaml.loader import SafeLoader
from src.yaml import LotDumper
from src import compare
import copy
from deepdiff import DeepDiff
from src.markdown import altair_to_urssaf

def build_lot(yml: str, md: str) -> str:
    """Build lot content file from md and yml data."""
    return "---\n" + (yml if isinstance(yml, str) else ''.join(yml)) + "---\n" + (md if isinstance(md, str) else ''.join(md)) + '\n'


def common_errors(lot: str):
    """Check and resolve common lot file errors."""
    with open(lot, 'r+', encoding=cst.encoding) as l__:
        lines = l__.readlines()
        line_index = 0
        while line_index < len(lines):
            line = lines[line_index]
            if search(r"\#{3}\t\[", line) is not None:
                lines[line_index] = sub(r"\#{3}\t\[", "### [", line)
            if line_index == 0:
                separator_len = len(list(filter(lambda l: l == '---\n', lines)))
                if line != '---\n' and separator_len < 2:
                    lines.insert(line_index, '---\n')
                    continue
                if search(r"^[ ]*\n$", line) is not None and separator_len == 2:
                    lines.pop(line_index)
                    line_index = 0
                    continue
            if line == '\n' and line_index + 1 < len(lines) and lines[line_index + 1] == '\n':
                lines.pop(line_index + 1)
                continue
            
            lines[line_index] = line.rstrip() + '\n'
            line_index += 1

        if not array_equal(l__.readlines(), lines, equal_nan=False):      
            l__.seek(0)
            l__.truncate()
            l__.writelines(lines)


def change_fichiers_images_path(lot):
    """Change fichier and images paths in markdown descriptions."""
    with open(lot, 'r', encoding=cst.encoding) as l__:
        txt = ''.join(l__.readlines())
    file_inclusion_regex = r"!?\[.*\]\([A-Za-z0-9\.\/\_\-]+\)"
    if search(file_inclusion_regex, txt):
        reg_result = findall(file_inclusion_regex, txt)
        for el in reg_result:
            file_path_regex = r"\([A-Za-z0-9\.\/\_\-]+\)"
            file_path = search(file_path_regex, el).group(0)[1:-1]
            entity = folders.get_last_folder(cst.images()) if is_image(file_path) else folders.get_last_folder(cst.fichiers())
            new_file_path = f"../../{entity}/{get_filename(file_path)}"
            new_el = sub(file_path_regex, '(' + new_file_path + ')', el)
            txt = txt.replace(el, new_el)
        txt = list(map(lambda f: f + '\n', txt.split('\n')))
        with open(lot, 'w', encoding=cst.encoding) as l__:
            l__.writelines(txt)


def change_fichiers_images_path_v2(lot: str, refs: list[dict[str, str]]):
    """Change references paths in files' markdown section."""
    with open(lot, 'r', encoding=cst.encoding) as l__:
        lines = l__.readlines()
    for pattern in refs:
        for line_index, _ in enumerate(lines):
            if pattern['rel'] in lines[line_index] and pattern['rel'] != pattern['update_rel']:
                lines[line_index] = lines[line_index].replace(pattern['rel'], pattern['update_rel'])
                cst.review_log.info(f"File '{get_filename(lot)}'\t" + \
                    ("\t" if cst.merged_tag in get_filename(lot) else "\t\t") + f"| Line {line_index + 1}\t| \
File reference changed : '{pattern['rel']}'\t->\t'{pattern['update_rel']}'")
    with open(lot, 'w', encoding=cst.encoding) as l__:
        l__.writelines(''.join(lines))


def try_open_yml(file: str):
    """
    Try to parse YML file.
    
    Parameters
    ----------
    file (str): file to open
    
    Returns
    -------
    errno, data (tuple):
    errno (int):
        - 0 -> no error
        - 1 -> parsing error
    data (any):
        - if no error -> data loaded
        - if error -> string error

    """
    data_yml = None
    data_md = None
    errno = 1
    try:
        with open(file, 'r', encoding=cst.encoding) as f__:
            # Extract yml part
            separated_parts = list(filter(lambda l: l != '', (''.join(f__.readlines())).split("---\n")))
            if len(separated_parts) > 0:
                data_yml = separated_parts[0]
            else:
                raise Exception("No YML part.")
            
            if len(separated_parts) > 1:
                data_md = separated_parts[1]
            else:
                data_md = ""

            data_yml = yaml.load(data_yml, Loader=SafeLoader)
            errno = 0
    except Exception as err:
        data_yml = str(err)
        data_md = str(err)
    
    return (errno, data_yml, data_md)


def no_regression(file: str, file_merged: str):
    """Check no regression between files -- old version --."""
    errno, data, md = try_open_yml(file)
    errno_merged, data_merged, md_merged = try_open_yml(file_merged)
    if errno == 0 and errno_merged == 0:
        data_ = check_main_keys(get_filename(file), copy.deepcopy(data))
        data_merged_ = check_main_keys(get_filename(file_merged), copy.deepcopy(data_merged))
        
        md_ = altair_to_urssaf(md)
        md_merged_ = altair_to_urssaf(md_merged)
        
        # Call v1 version or v2 version -- non-regression
        (data_, data_merged_) = eval(f'compare_and_modify_{cst.version}')(copy.deepcopy(data_), copy.deepcopy(data_merged_))
       
        if DeepDiff(data, data_, ignore_order=True) or DeepDiff(md, md_, ignore_order=True):
            with open(file, 'w', encoding=cst.encoding) as f__:
                f__.write(build_lot(yml=yaml.dump(data_, sort_keys=False, Dumper=LotDumper, allow_unicode=True,\
                    width=float("inf")), md=md_))
        
        if DeepDiff(data_merged, data_merged_, ignore_order=True) or DeepDiff(md_merged, md_merged_, ignore_order=True):
            with open(file_merged, 'w', encoding=cst.encoding) as f__:
                f__.write(build_lot(yml=yaml.dump(data_merged_, sort_keys=False, Dumper=LotDumper, allow_unicode=True,\
                    width=float("inf")), md=md_merged_))


def check_lot_key(filename: str, data: any):
    """Check lot name is correct."""
    old_fn = data[cst.lot]['nom']
    
    new_fn = (filename.split('.')[0]).split('_')
    new_fn[0] = new_fn[0] + cst.project.split('_')[-1].upper()
    new_fn = ('_'.join(new_fn)).replace('_' + cst.merged_tag, '')

    data[cst.lot] = {
        'nom': new_fn
    }
    
    if old_fn != new_fn:
        local_fn = get_filename(filename)
        cst.review_log.info(msg=f"Categorie: No regression -> File {local_fn}\
\t" + ("\t\t" if cst.merged_tag not in local_fn else "") + f"| Key: lot.nom\t\t| Cause: {old_fn} -> {new_fn}")

    return data


def check_main_keys(filename: str, data: any):
    """Check yaml get all important keys and add them otherwise."""
    for key, _ in cst.keys.items():
        if key not in data.keys():
            data[key] = cst.keys[key]
            local_fn = get_filename(filename)
            cst.review_log.info(msg=f"Categorie: No regression -> File {local_fn}\
\t" + ("\t\t" if cst.merged_tag not in local_fn else "") + f"| Adding {key} = {data[key]} to YAML | Cause : Missing main key")
        else:
            if compare.is_empty_(data[key]):
                data[key] = []
                
    data[cst.livrables] = list(filter(lambda liv: str(liv['nom']).upper() != "N/A", data[cst.livrables]))
    
    if len(list(filter(lambda liv: str(liv['type']).lower() == 'rpm', data[cst.livrables]))) == 0:
        list(data[cst.livrables]).append({ 'type': 'rpm', 'nom': None, 'version': None})
    
    if cst.lot not in data.keys() or cst.lot in data.keys() and 'nom' not in data[cst.lot].keys():
        data[cst.lot] = { 'nom': '' }
        local_fn = get_filename(filename)
        cst.review_log.info(msg=f"Categorie: No regression -> File {local_fn}\
\t" + ("\t\t" if cst.merged_tag not in local_fn else "") + f"| Adding `{cst.lot}.nom` to YAML | Cause : Missing main key `{cst.lot}.nom`")
        
    data = check_lot_key(filename, data)
    return data


def compare_and_modify_v1(data, data_merged):
    """Compare datas & modify datas. --- old compare ---."""
    data, data_merged = compare.c_livrables(data, data_merged)
            
    data, data_merged = compare.c_bases(data, data_merged)   
    
    data, data_merged = compare.c_tokens(data, data_merged)
     
    data, data_merged = compare.c_targets(data, data_merged)

    return (data, data_merged)
