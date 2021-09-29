import sys

from flask import render_template

from slddb.constants import Cu_kalpha, Mo_kalpha, r_e, r_e_angstrom
from slddb import SLDDB, DB_FILE
from slddb.material import Material, Formula

from numpy import nan_to_num
import base64
from io import BytesIO
from matplotlib.figure import Figure

def get_graph(E, real, imag, name='Iron'):
    # Generate the figure **without using pyplot**.
    fig = Figure()
    ax = fig.subplots()
    ax.plot(E,  real/r_e_angstrom, label='Re')
    ax.plot(E, -imag/r_e_angstrom, label='-Im')
    ax.legend()
    ax.set_xscale('log')
    ax.set_xlabel('E (keV)')
    ax.set_ylabel('electron density (rₑ/Å³)')
    ax.set_title('X-Ray optical parameters for %s'%name)
    twin=ax.twinx()
    ymin, ymax=ax.get_ylim()
    twin.set_ylim(ymin*r_e*10., ymax*r_e*10)
    twin.set_ylabel('SLD (10⁻⁶ Å⁻²)')
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    fig.tight_layout()
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f'<img style="width: 40em; max-width: 100%;" src="data:image/png;base64,{data}" />'

def calculate_selection(ID):
    db=SLDDB(DB_FILE)
    res=db.search_material(ID=ID, filter_invalid=False)
    try:
        material=db.select_material(res[0])
    except Exception as e:
        return render_template('base.html', error=repr(e)+'<br >'+"Raised when tried to parse material = %s"%res[0])
    E, rho_x=material.rho_vs_E()
    _, delta=material.delta_vs_E()
    _, beta=material.beta_vs_E()
    script=get_graph(E, rho_x.real, rho_x.imag, res[0]['name'])
    if 'H' in material.formula:
        dformula=Formula(material.formula)
        Hidx=dformula.index('H')
        dformula[Hidx]=('D', dformula[Hidx][1])
        deuterated=Material([(db.elements.get_element(element), amount) for element, amount in dformula],
                             fu_dens=material.fu_dens)
    else:
        deuterated=None
    return render_template('sldcalc.html', material=material, material_name=res[0]['name'],
                           material_description=res[0]['description'], deuterated=deuterated,
                           script=script, xray_E=E.tolist(),
                           xray_rho_real=nan_to_num(rho_x.real).tolist(),
                           xray_rho_imag=nan_to_num(rho_x.imag).tolist(),
                           xray_delta=nan_to_num(delta).tolist(), xray_beta=nan_to_num(beta).tolist(),
                           validated=res[0]['validated'], validated_by=res[0]['validated_by'],
                           invalid=res[0]['invalid'], invalid_by=res[0]['invalid_by'],
                           formula=res[0]['formula'], density=material.dens, mu=material.mu)

def calculate_user(formula, density, mu, density_choice, mu_choice):
    db=SLDDB(DB_FILE)
    kwrds={}
    if density==0:
        return render_template('sldcalc.html', error="Density can not be zero!")
    if density_choice=='density':
        kwrds['dens']=density
    elif density_choice=='volume':
        kwrds['fu_volume']=density
    elif density_choice=='FUdens':
        kwrds['fu_dens']=density
    elif density_choice=='FUdnm':
        kwrds['fu_dens']=density*1e-3

    if mu_choice=='muB':
        kwrds['mu']=mu
    elif mu_choice=='magn':
        kwrds['M']=mu
    try:
        m=Material([(db.elements.get_element(element), amount) for element, amount in formula], **kwrds)
    except Exception as e:
        return render_template('sldcalc.html', error=repr(e))
    else:
        E, rho_x=m.rho_vs_E()
        _, delta=m.delta_vs_E()
        _, beta=m.beta_vs_E()
        script=get_graph(E, rho_x.real, rho_x.imag, str(formula))
        if 'H' in m.formula:
            dformula=Formula(m.formula)
            Hidx=dformula.index('H')
            dformula[Hidx]=('D', dformula[Hidx][1])
            deuterated=Material([(db.elements.get_element(element), amount) for element, amount in dformula],
                                fu_dens=m.fu_dens)
        else:
            deuterated=None
        return render_template('sldcalc.html', material=m, deuterated=deuterated,
                           material_name="User input",
                           material_description="", script=script, xray_E=E.tolist(),
                           xray_rho_real=nan_to_num(rho_x.real).tolist(),
                           xray_rho_imag=nan_to_num(rho_x.imag).tolist(),
                           xray_delta=nan_to_num(delta).tolist(), xray_beta=nan_to_num(beta).tolist())

def validate_selection(ID, user):
    db=SLDDB(DB_FILE)
    db.validate_material(ID, user)
    return calculate_selection(ID)

def invalidate_selection(ID, user):
    db=SLDDB(DB_FILE)
    db.invalidate_material(ID, user)
    return calculate_selection(ID)
