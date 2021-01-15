from flask import render_template

from slddb.constants import Cu_kalpha, Mo_kalpha
from slddb import SLDDB, DB_FILE
from slddb.material import Material, Formula

try:
    from .flask_embed import get_script
except ImportError:
    def get_script(*args): return ''


def calculate_selection(ID):
    db=SLDDB(DB_FILE)
    res=db.search_material(ID=ID)
    try:
        material=db.select_material(res[0])
    except Exception as e:
        return render_template('base.html', result_table=repr(e)+'<br >'+
                                                         "Raised when tried to parse material = %s"%res[0])
    E, delta=material.delta_vs_E()
    script=get_script(E, delta.real, delta.imag)
    return render_template('sldcalc.html', material=material, material_name=res[0]['name'],
                           material_description=res[0]['description'], Cu_kalpha=Cu_kalpha,
                           Mo_kalpha=Mo_kalpha, script=script,
                           formula=res[0]['formula'], density=material.dens, mu=material.mu)

def calculate_user(formula, density, is_density, mu):
    db=SLDDB(DB_FILE)
    try:
        if is_density:
            m=Material([(db.elements.get_element(element), amount) for element, amount in formula],
                   dens=density, mu=mu)
        else:
            m=Material([(db.elements.get_element(element), amount) for element, amount in formula],
                       fu_volume=density, mu=mu)
    except Exception as e:
        return render_template('sldcalc.html', result_table=repr(e)+'<br/>'+str(f))
    else:
        E, delta=m.delta_vs_E()
        script=get_script(E, delta.real, delta.imag)
        return render_template('sldcalc.html', material=m, material_name="User input",
                           material_description="", Cu_kalpha=Cu_kalpha,
                           Mo_kalpha=Mo_kalpha, script=script)

