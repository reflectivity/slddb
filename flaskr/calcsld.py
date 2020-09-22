from flask import render_template

from slddb.constants import Cu_kalpha, Mo_kalpha
from slddb import SLDDB, DB_FILE
from slddb.material import Material, Formula

try:
    from .flask_embed import get_script
except ImportError:
    def get_script(*args): return ''


def result_table(material, name, description=""):
    out='<table class="withborder">\n'
    out+='    <tr><td>Compound</td><td colspan=2>%s</td></tr>\n'%name
    out+='    <tr><td>Description</td><td colspan=2 syle="word-wrap;">%s</td></tr>\n'%description
    out+='    <tr><td>Chemical Formula</td><td colspan=2>%s</td></tr>\n'%str(material)
    out+='    <tr><td>Density (g/cm³)</td><td colspan=2>%.4f</td></tr>\n'%material.dens
    out+='    <tr><td>Neutron nuclear SLD (10⁻⁶ Å⁻²)</td><td>%s</td><td>%s</td></tr>\n'%("%.6f"%(1e6*material.rho_n.real),
                                                        "%.6f"%(1e6*material.rho_n.imag))
    out+='    <tr><td>Neutron magnetic SLD (10⁻⁶ Å⁻²)</td><td colspan=2>%s</td></tr>\n'%("%.6f"%(1e6*material.rho_m),)
    sldx=material.delta_of_E(Cu_kalpha)
    out+='    <tr><td>Cu-Kɑ SLD (10⁻⁶ Å⁻²)</td><td>%s</td><td>%s</td></tr>\n'%("%.6f"%(1e6*sldx.real),
                                                        "%.6f"%(1e6*sldx.imag))
    sldx=material.delta_of_E(Mo_kalpha)
    out+='    <tr><td>Mo-Kɑ SLD (10⁻⁶ Å⁻²)</td><td>%s</td><td>%s</td></tr>\n'%("%.6f"%(1e6*sldx.real),
                                                        "%.6f"%(1e6*sldx.imag))
    out+='</table>'
    return out

def calculate_selection(ID):
    db=SLDDB(DB_FILE)
    res=db.search_material(ID=ID)
    try:
        material=db.select_material(res[0])
    except Exception as e:
        return render_template('base.html', result_table=repr(e)+'<br >'+
                                                         "Raised when tried to parse material = %s"%res[0])
    out=result_table(material, res[0]['name'], res[0]['description'])
    E, delta=material.delta_vs_E()
    script=get_script(E, delta.real, delta.imag)
    return render_template('sldcalc.html', result_table=out, script=script,
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
        out=result_table(m, "User input")
        E, delta=m.delta_vs_E()
        script=get_script(E, delta.real, delta.imag)
        return render_template('sldcalc.html', result_table=out, script=script)

