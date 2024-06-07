"""Compare datas modules."""
import src.constants as cst
from packaging import version

def is_empty_(data):
    """Check if data is empty."""
    if isinstance(data, dict): return False
    
    if data is None or len(data) == 0 or (len(data) == 1 and str(data[0]['nom']).upper() == 'N/A'):
        return True
    return False

def v__sup__(v1: dict, v2: dict):
    """Check version key."""
    if 'version' not in v1:
        return (None, "Missing key word 'version'", 0)
    if 'version' not in v2:
        return (None, "Missing key word 'version'", 1)
    
    v1__ = v2__ = None
    
    try:
        v1__ = version.parse(str(v1['version']).split('-')[0])
    except Exception:
        return (None, "Unparsable version", 0)
    
    try:
        v2__ = version.parse(str(v2['version']).split('-')[0])
    except Exception:
        return (None, "Unparsable version", 1)
    
    return (v1__ > v2__, None, None)


def c_livrables(data, data_merged):
    """Compare and returne modify livrables key."""
    if is_empty_(data[cst.livrables]):
        data[cst.livrables] = []

    if is_empty_(data_merged[cst.livrables]):
        data_merged[cst.livrables] = []
    
    for livrable in data[cst.livrables]:
        if livrable['nom'] not in list(map(lambda liv: liv['nom'], data_merged[cst.livrables])):
            data_merged[cst.livrables].append(livrable)
            cst.review_log.warning(msg=f"Categorie: No regression -> Lot: {data_merged[cst.lot]['nom']} \
| Key: {cst.livrables}.{livrable['nom']} | Cause: Missing element")
        else:
            new_livrable = list(filter(lambda el: el['nom'] == livrable['nom'], data_merged[cst.livrables]))[0]
            # if version.parse(livrable['version'].split('-')[0]) > version.parse(new_livrable['version'].split('-')[0]):
            v_compare, err_msg, err_el = v__sup__(livrable, new_livrable)
            if v_compare is not None:
                if v_compare is True:
                    for l__ in data_merged[cst.livrables]:
                        if l__['nom'] == livrable['nom']:
                            cst.review_log.warning(msg=f"Categorie: No regression -> Lot: {data_merged[cst.lot]['nom']} \
| Key: {cst.livrables}.{livrable['nom']}.version | Cause: {new_livrable['version']} -> {livrable['version']}")
                            l__['version'] = livrable['version']
            else:
                if err_el == 0: err_el__ = livrable
                else: err_el__ = new_livrable
                cst.review_log.error(msg=f"Categorie: No regression -> Lot: {(data if err_el == 0 else data_merged)[cst.lot]['nom']} \
| Key: {cst.livrables}.{err_el__['nom']}.version | Cause: {err_msg}")
            
    return data, data_merged


def c_bases(data, data_merged):
    """Compare and returne modify bases key."""
    if is_empty_(data[cst.bases]):
        data[cst.bases] = []

    if is_empty_(data_merged[cst.bases]):
        data_merged[cst.bases] = []
    
    for base in data[cst.bases]:
        if base['nom'] not in list(map(lambda ba: ba['nom'], data_merged[cst.bases])):
            data_merged[cst.bases].append(base)
            cst.review_log.warning("Categorie: No regression -> Lot: %s \
| Key: %s | Cause: Missing element", data_merged[cst.lot]['nom'], cst.bases + '.' + base['nom'])
        base_merged = list(filter(lambda ba: ba['nom'] == base['nom'], data_merged[cst.bases]))[0]
        if 'update' in base.keys():
            if base['update'] is True:
                if 'update' in base_merged.keys() and base_merged['update'] is False or 'update' not in base_merged.keys():
                    for b in data_merged[cst.bases]:
                        if b['nom'] == base['nom']: 
                            b['update'] = True
                    cst.review_log.warning("Categorie: No regression -> Lot: %s | Key: %s \
| Cause: `Update` set to True", data_merged[cst.lot]['nom'], cst.bases + '.' + base['nom'])
        else:
            base['update'] = False
            for b in data_merged[cst.bases]:
                if b['nom'] == base['nom']: 
                    b['update'] = True
                    cst.review_log.warning("Categorie: No regression -> Lot: %s | Key: %s \
| Cause: `Update` set to True", data_merged[cst.lot]['nom'], cst.bases + '.' + base['nom'])
        v_compare, _, _ = v__sup__(base, base_merged)
        if v_compare is not None:
            if v_compare is True:
                for b in data_merged[cst.bases]:
                    if b['nom'] == base['nom']:
                        cst.review_log.warning("Categorie: No regression -> Lot: %s | Key: %s \
| Cause: Version BDD set to %s", data_merged[cst.lot]['nom'], cst.bases + '.' + base['nom'] + '.version', base['version'])
                        b['version'] = base['version']
        else:
            if 'version' not in base:
                base['version'] = "0"
            if 'version' not in base_merged:
                for b in data_merged[cst.bases]:
                    if b['nom'] == base['nom']:
                        b['version'] = base['version'] if 'version' in base else '0'
    
    return data, data_merged


def c_tokens(data, data_merged):
    """Compare and returne modify tokens key."""
    if is_empty_(data[cst.tokens]):
        data[cst.tokens] = []

    if is_empty_(data_merged[cst.tokens]):
        data_merged[cst.tokens] = []
        
    for token in data[cst.tokens]:
        if token['nom'] not in list(map(lambda to: to['nom'], data_merged[cst.tokens])):
            data_merged[cst.tokens].append(token)
            cst.review_log.warning("Categorie: No regression -> Lot: %s | Key: %s\t\t\
| Cause: Missing element", data_merged[cst.lot]['nom'], cst.tokens + '.' + token['nom'])
    
    return data, data_merged


def c_targets(data, data_merged):
    """Compare and returne modify targets key."""
    for server_name in data[cst.targets].keys():
        if server_name not in data_merged[cst.targets].keys():
            data_merged[cst.targets][server_name] = data[cst.targets][server_name]
            cst.review_log.warning("Categorie: No regression -> Lot: %s | Key: %s\t\t\
| Cause: Missing element.", data_merged[cst.lot]['nom'], cst.targets + '.' + server_name + '.*')
        else:
            for target in data[cst.targets][server_name]:
                if target not in data_merged[cst.targets][server_name]:
                    data_merged[cst.targets][server_name].append(target)
                    cst.review_log.warning("Categorie: No regression -> Lot: %s | Key: %s\t\t\
| Cause: Missing element", data_merged[cst.lot]['nom'], cst.targets + '.' + server_name + '.' + target)

    return data, data_merged