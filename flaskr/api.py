import json

from .blender import collect_protein, collect_dna, collect_rna
from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup
from slddb.constants import Cu_kalpha, Mo_kalpha, r_e
from slddb.material import Material, Formula


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
    out={}
    out['ID']=None
    out['name']=name
    out['formula']=str(material.formula)
    out['density']=material.dens
    out['fu_dens']=material.fu_dens
    out['fu_volume']=material.fu_volume
    out['fu_mass']=material.fu_mass
    out['fu_b']=repr(material.fu_b)
    out['rho_n']=repr(material.rho_n)
    out['rho_n_mag']=repr(material.rho_m)
    out['mu']=material.mu
    out['M']=material.M
    out['rho_Cu_kalpha']=repr(material.rho_of_E(Cu_kalpha))
    out['rho_Mo_kalpha']=repr(material.rho_of_E(Mo_kalpha))
    E,delta=material.rho_vs_E()
    out['xray_E']=E.tolist()
    out['xray_delta_real']=delta.real.tolist()
    out['xray_delta_imag']=delta.imag.tolist()
    out['units']={'density': 'g/cm**3', 'fu_dens': '1/angstrom**3', 'fu_volume': 'angstrom**3', 'fu_mass': 'u',
                  'fu_b': 'fm', 'rho_n': '1/angstrom**2', 'rho_n_mag': '1/angstrom**2', 'mu': 'muB', 'M': 'emu/cm**3',
                  'xray_E': 'keV', 'xray_values': '1/angstrom**2'}
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

    xru=args.get('xray_unit', 'edens')

    out={}
    if res[0]['invalid'] is not None:
        out['WARNING']='This entry has been invalidated by ORSO on %s, please contact %s for more information.'%(
            res[0]['invalid'], res[0]['invalid_by'])
    out['ID']=int(args['ID'])
    out['ORSO_validated']=res[0]['validated'] is not None
    out['reference']=res[0].get('reference', '')
    out['doi']=res[0].get('doi', '')
    out['name']=res[0]['name']
    out['formula']=str(material.formula)
    out['density']=material.dens
    out['fu_dens']=material.fu_dens
    out['fu_volume']=material.fu_volume
    out['fu_mass']=material.fu_mass
    out['fu_b']=repr(material.fu_b)
    out['rho_n']=repr(material.rho_n)
    out['rho_n_mag']=material.rho_m
    out['mu']=material.mu
    out['M']=material.M
    if xru=='n_db':
        out['delta_Cu_kalpha']=material.delta_of_E(Cu_kalpha)
        out['beta_Cu_kalpha']=material.beta_of_E(Cu_kalpha)
        out['delta_Mo_kalpha']=material.delta_of_E(Mo_kalpha)
        out['beta_Mo_kalpha']=material.beta_of_E(Mo_kalpha)
        E, delta=material.delta_vs_E()
        E, beta=material.beta_vs_E()
        out['xray_E']=E.tolist()
        out['xray_delta']=delta.tolist()
        out['xray_beta']=beta.tolist()
    else:
        if xru=='edens':
            factor=1.0e5/r_e
        else:
            factor=1.0
        out['rho_Cu_kalpha']=repr(factor*material.rho_of_E(Cu_kalpha))
        out['rho_Mo_kalpha']=repr(factor*material.rho_of_E(Mo_kalpha))
        E, rho=material.rho_vs_E()
        out['xray_E']=E.tolist()
        out['xray_real']=(factor*rho).real.tolist()
        out['xray_imag']=(factor*rho).imag.tolist()
    out['units']={'density': 'g/cm**3', 'fu_dens': '1/angstrom**3', 'fu_volume': 'angstrom**3', 'fu_mass': 'u',
                  'fu_b': 'fm', 'rho_n': '1/angstrom**2', 'rho_n_mag': '1/angstrom**2', 'mu': 'muB', 'M': 'emu/cm**3',
                  'xray_E': 'keV'}
    if xru=='n_db':
        out['units']['xray_values']='1'
    elif xru=='edens':
        out['units']['xray_values']='r_e/angstrom**3'
    else:
        out['units']['xray_values']='1/angstrom**2'
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
