import json

from slddb.blender import collect_protein, collect_dna, collect_rna
from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup
from slddb.material import Material, Formula


def calc_api(args):
    """Calculate SLD from formula/density or biological sequence.

    args: dict-like with optional keys: formula, density, protein, dna, rna,
          name, material_description, xray_unit.
    Returns a JSON string.
    """
    if 'protein' in args:
        try:
            material = collect_protein(args['protein'])
        except Exception as e:
            return repr(e)
        else:
            name = args.get('name', 'protein')
    elif 'dna' in args:
        try:
            material = collect_dna(args['dna'])
        except Exception as e:
            return repr(e)
        else:
            name = args.get('name', 'DNA')
    elif 'rna' in args:
        try:
            material = collect_rna(args['rna'])
        except Exception as e:
            return repr(e)
        else:
            name = args.get('name', 'RNA')
    elif 'formula' in args and 'density' in args:
        f = Formula(args['formula'], sort=False)
        try:
            material = Material(f, dens=float(args['density']))
        except Exception as e:
            return repr(e)
        else:
            name = args.get('name', 'User Query')
    else:
        return 'Could not calculate, missing formula and density or protein/dna/rna sequence'
    material.name = name
    if args.get('material_description', '') != '':
        material.extra_data['description'] = args['material_description']
    out = material.export(xray_units=args.get('xray_unit', 'edens'))
    return out


def select_api(args):
    """Return JSON for a material selected by ID.

    args: dict-like with keys: ID, and optionally xray_unit.
    Returns a JSON string.
    """
    db = SLDDB(DB_FILE)
    res = db.search_material(filter_invalid=False, ID=int(args['ID']))
    try:
        material = db.select_material(res[0])
    except IndexError:
        return '## ID not found in database'
    except Exception as e:
        return repr(e) + '<br >' + "Raised when tried to parse material = %s" % res[0]
    out = material.export(xray_units=args.get('xray_unit', 'edens'))
    return out

def search_api(args):
    """Search the database with the given field values.

    args: dict-like mapping DB field names to query values.
    Returns a JSON string.
    """
    query = {}
    for key, value in args.items():
        if str(value).strip() == '':
            continue
        if key in DB_MATERIALS_FIELDS:
            try:
                query[key] = db_lookup[key][1].convert(str(value))
            except Exception as e:
                return repr(e) + '<br >' + "Raised when tried to parse %s = %s" % (key, value)
    db = SLDDB(DB_FILE)
    res = db.search_material(serializable=True, limit=10000, **query)

    # remove hidden database fields besides ORSO validation
    for ri in res:
        for field in DB_MATERIALS_HIDDEN_DATA:
            if field.startswith('validated'):
                continue
            del ri[field]

    return res


def query_api(args):
    """Dispatch an API request based on which keys are present in args.

    args: dict-like (e.g. request.args or a plain dict).
    Returns a JSON string.
    """
    if 'ID' in args:
        return select_api(args)
    elif 'sldcalc' in args:
        return calc_api(args)
    elif 'get_fields' in args:
        return [
            field for field in DB_MATERIALS_FIELDS if field not in DB_MATERIALS_HIDDEN_DATA
        ]
    else:
        return search_api(args)
