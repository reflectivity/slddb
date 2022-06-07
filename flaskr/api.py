import json

from .blender import collect_protein, collect_dna, collect_rna
from orsopy.slddb import SLDDB, DB_FILE
from orsopy.slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup
from orsopy.slddb.constants import Cu_kalpha, Mo_kalpha, r_e
from orsopy.slddb.material import Material, Formula


def calc_api(args):
    if 'protein' in args:
        try:
            material=collect_protein(args['protein'])
        except Exception as e:
            return repr(e)
        else:
            name=args.get('name', default='protein')
    elif 'dna' in args:
        try:
            material=collect_dna(args['dna'])
        except Exception as e:
            return repr(e)
        else:
            name=args.get('name', default='DNA')
    elif 'rna' in args:
        try:
            material=collect_rna(args['rna'])
        except Exception as e:
            return repr(e)
        else:
            name=args.get('name', default='RNA')
    elif 'formula' in args and 'density' in args:
        f=Formula(args['formula'], sort=False)
        try:
            material=Material(f, dens=float(args['density']))
        except Exception as e:
            return repr(e)
        else:
            name=args.get('name', default='User Query')
    else:
        return 'Could not calculate, missing formula and density or protein/dna/rna sequence'
    material.name=name
    if args.get('material_description', default='')!='':
        material.extra_data['description']=args['material_description']
    out = material.export(xray_units=args.get('xray_unit', 'edens'))
    return json.dumps(out, indent='    ')

def select_api(args):
    db=SLDDB(DB_FILE)
    res=db.search_material(filter_invalid=False, ID=int(args['ID']))
    try:
        material=db.select_material(res[0])
    except IndexError:
        return '## ID not found in database'
    except Exception as e:
        return repr(e)+'<br >'+"Raised when tried to parse material = %s"%res[0]

    out=material.export(xray_units=args.get('xray_unit', 'edens'))
    return json.dumps(out, indent='    ')

def search_api(args):
    query={}
    for key, value in args.items():
        if value.strip() == '':
            continue
        if key in DB_MATERIALS_FIELDS:
            try:
                query[key]=db_lookup[key][1].convert(value)
            except Exception as e:
                return repr(e)+'<br >'+"Raised when tried to parse %s = %s"%(key, value)
    db=SLDDB(DB_FILE)
    res=db.search_material(serializable=True, limit=10000, **query)

    # remove hidden database fields besides ORSO validation
    for ri in res:
        for field in DB_MATERIALS_HIDDEN_DATA:
            if field.startswith('validated'):
                continue
            del ri[field]

    return json.dumps(res, indent='    ')
