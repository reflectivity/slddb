import json

from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup
from slddb.constants import Cu_kalpha, Mo_kalpha
from slddb.material import Material, Formula


def calc_api(args):
    if 'formula' in args and 'density' in args:
        f=Formula(args['formula'], sort=False)
        db=SLDDB(DB_FILE)
        try:
            material=Material([(db.elements.get_element(element), amount) for element, amount in f],
                   dens=float(args['density']))
        except Exception as e:
            return repr(e)
        else:
            out={}
            out['ID']=None
            out['name']='User Query'
            out['formula']=str(material)
            out['density']=material.dens
            out['rho_n']=repr(material.rho_n)
            out['rho_n_mag']=repr(material.rho_m)
            out['rho_Cu_kalpha']=repr(material.delta_of_E(Cu_kalpha))
            out['rho_Mo_kalpha']=repr(material.delta_of_E(Mo_kalpha))
            E,delta=material.delta_vs_E()
            out['xray_E']=E.tolist()
            out['xray_delta_real']=delta.real.tolist()
            out['xray_delta_imag']=delta.imag.tolist()
            return json.dumps(out)

def select_api(args):
    db=SLDDB(DB_FILE)
    res=db.search_material(ID=int(args['ID']))
    try:
        material=db.select_material(res[0])
    except Exception as e:
        return repr(e)+'<br >'+"Raised when tried to parse material = %s"%res[0]

    out={}
    out['ID']=res[0]['name']
    out['name']=res[0]['name']
    out['formula']=str(material)
    out['density']=material.dens
    out['rho_n']=repr(material.rho_n)
    out['rho_n_mag']=repr(material.rho_m)
    out['rho_Cu_kalpha']=repr(material.delta_of_E(Cu_kalpha))
    out['rho_Mo_kalpha']=repr(material.delta_of_E(Mo_kalpha))
    E, delta=material.delta_vs_E()
    out['xray_E']=E.tolist()
    out['xray_delta_real']=delta.real.tolist()
    out['xray_delta_imag']=delta.imag.tolist()
    return json.dumps(out)

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
    res=db.search_material(serializable=True, **query)

    return json.dumps(res)
