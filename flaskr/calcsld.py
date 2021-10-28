import sys
import traceback

from flask import render_template

from slddb.constants import Cu_kalpha, Mo_kalpha, r_e, r_e_angstrom
from slddb import SLDDB, DB_FILE
from slddb.material import Material, Formula, H2O, D2O
from slddb.element_table import get_element

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

def get_deuteration_graph(m: Material, name=None):
    # Generate a graph for matching H2O/D2O with the given material
    if name is None:
        name=str(m.formula)
    mpoint=m.not_exchanged.match_point

    fig = Figure()
    ax = fig.subplots()
    ax.plot([0,100], [m.rho_n.real*1e6, m.rho_n.real*1e6], label=name, color='C0')
    ax.plot([0,100], [H2O.rho_n.real*1e6, D2O.rho_n.real*1e6], label='Water', color='C1')
    if mpoint>=0 and mpoint<=1:
        ax.plot([100*mpoint, 100*mpoint], [H2O.rho_n.real*1e6, m.rho_n.real*1e6], '--',
                label='Contrast Matched', color='C1')
        ax.text(100*mpoint, m.rho_n.real*1e6, '%.1f%%'%(100*mpoint), va='bottom', ha='right')
    if 'Hx' in m.formula:
        # create material where 90% exchangable sites are replace by deuterium
        md=m.exchange(0., 1.0, exchange=0.9)
        ax.plot([0,100], [m.rho_n.real*1e6, md.rho_n.real*1e6],
                label='90% exchange', color='C2')
        mpoint2=m.match_exchange(0., exchange=0.9)
        if mpoint2>=0 and mpoint2<=1:
            mrho=mpoint2*md.rho_n.real+(1-mpoint2)*m.rho_n.real
            ax.plot([100*mpoint2, 100*mpoint2], [H2O.rho_n.real*1e6, mrho*1e6], '--',
                    label='Contrast Matched', color='C2')
            ax.plot([0*mpoint2, 100*mpoint2], [mrho*1e6, mrho*1e6], '--', color='C2')
            ax.text(100*mpoint2, mrho*1e6, '%.3f | %.1f%%'%(mrho*1e6, 100*mpoint2), va='bottom', ha='right')

    ax.legend()
    ax.set_xlabel('Water deuteration %')
    ax.set_ylabel('SLD (10⁻⁶ Å⁻²)')
    ax.set_title('Contrast matching of %s'%name)
    ax.set_xlim([0., 100.])
    ax.set_ylim([H2O.rho_n.real*1e6, D2O.rho_n.real*1e6])
    # Save it to a temporary buffer.
    buf = BytesIO()
    fig.savefig(buf, format="png")
    fig.tight_layout()
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f'<img style="width: 40em; max-width: 100%;" src="data:image/png;base64,{data}" />'

def get_absorption_graph(m: Material, name=None):
    # Generate a graph for matching H2O/D2O with the given material
    if name is None:
        name=str(m.formula)

    fig = Figure()
    ax = fig.subplots()
    L,rho_n=m.rho_n_vs_L()
    ax.semilogx(L, -rho_n.imag*1e6)
    ax.set_xlabel('Wavelength [Å]')
    ax.set_ylabel('-Im(SLD) (10⁻⁶ Å⁻²)')
    ax.set_title('Wavelength dependant absorption part of %s'%name)
    ax.set_xlim([0.2, 20.])
    ax.grid()
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
    match_point=0.
    E, rho_x=material.rho_vs_E()
    _, delta=material.delta_vs_E()
    _, beta=material.beta_vs_E()
    script=get_graph(E, rho_x.real, rho_x.imag, res[0]['name'])
    if 'H' in material.formula or 'Hx' in material.formula:
        deuterated=material.deuterated
        if 'Hx' in material.formula:
            exchanged=material.exchanged
            match_point = 100.*material.match_exchange()
        else:
            exchanged=None
    else:
        deuterated=None
        exchanged=None
    if 'H' in material.formula or 'Hx' in material.formula or 'D' in material.formula \
            or any([tag in res[0].get('tags', []) for tag in
                    ['polymer', 'biology', 'membrane', 'lipid', 'small organic', 'surfactant', 'protein']]):
        script = '<table><tr><td colspan="2">' \
                 '<button type="button" class="collapsible">Toggle graph: Contrast Matching/X-Ray</button>' \
                 '</td></tr><tr><td class="uncollapsed">%s</td></tr>' \
                 '<tr><td class="collapsed">%s</td></tr></table>'%(script,
                                                   get_deuteration_graph(material, name=res[0]['name']))
    elif material.has_ndata:
        # wavlength dependant absopriton
        script = '<table><tr><td colspan="2">' \
                 '<button type="button" class="collapsible">Toggle graph: Neutron Absorption/X-Ray</button>' \
                 '</td></tr><tr><td class="uncollapsed">%s</td></tr>' \
                 '<tr><td class="collapsed">%s</td></tr></table>'%(script,
                                                               get_absorption_graph(material, name=res[0]['name']))
    return render_template('sldcalc.html', material=material, material_name=res[0]['name'],
                           material_description=res[0]['description'], deuterated=deuterated,
                           exchanged=exchanged, match_point=match_point,
                           script=script, xray_E=E.tolist(),
                           xray_rho_real=nan_to_num(rho_x.real).tolist(),
                           xray_rho_imag=nan_to_num(rho_x.imag).tolist(),
                           xray_delta=nan_to_num(delta).tolist(), xray_beta=nan_to_num(beta).tolist(),
                           validated=res[0]['validated'], validated_by=res[0]['validated_by'],
                           invalid=res[0]['invalid'], invalid_by=res[0]['invalid_by'],
                           formula=res[0]['formula'], density=material.dens, mu=material.mu)

def calculate_user(formula, density, mu, density_choice, mu_choice, name=None, material_description=""):
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
        material=Material([(get_element(element), amount) for element, amount in formula], **kwrds)
    except Exception as e:
        traceback.print_exc()
        return render_template('sldcalc.html', error=repr(e))
    else:
        match_point=0.0
        E, rho_x=material.rho_vs_E()
        _, delta=material.delta_vs_E()
        _, beta=material.beta_vs_E()
        script=get_graph(E, rho_x.real, rho_x.imag, name or str(formula))
        if 'H' in material.formula or 'Hx' in material.formula or 'D' in material.formula:
            deuterated=material.deuterated
            if 'Hx' in material.formula:
                exchanged=material.exchanged
                match_point = 100.*material.match_exchange()
            else:
                exchanged=None
        else:
            deuterated=None
            exchanged=None
        if 'H' in material.formula or 'Hx' in material.formula or 'D' in material.formula:
            script = '<table><tr><td colspan="2">' \
                     '<button type="button" class="collapsible">Toggle graph: Contrast Matching/X-Ray</button>' \
                     '</td></tr><tr><td class="uncollapsed">%s</td></tr>' \
                     '<tr><td class="collapsed">%s</td></tr></table>'%(script, get_deuteration_graph(material, name=name))
        elif material.has_ndata:
            # wavlength dependant absopriton
            script = '<table><tr><td colspan="2">' \
                     '<button type="button" class="collapsible">Toggle graph: Neutron Absorption/X-Ray</button>' \
                     '</td></tr><tr><td class="uncollapsed">%s</td></tr>' \
                     '<tr><td class="collapsed">%s</td></tr></table>'%(script,
                                                                       get_absorption_graph(material, name=name))
        return render_template('sldcalc.html', material=material, deuterated=deuterated,
                           exchanged=exchanged, match_point=match_point,
                           material_name=name or "User input",
                           material_description=material_description, script=script, xray_E=E.tolist(),
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
