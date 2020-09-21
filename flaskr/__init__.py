import json
from flask import Flask
from flask import request, render_template

from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup
from slddb.constants import Cu_kalpha, Mo_kalpha
from slddb.material import Material, Formula

try:
    from .flask_embed import get_script
except ImportError:
    def get_script(*args): return ''

app=Flask("ORSO SLD Data Base", template_folder='flaskr/templates',
          static_folder='flaskr/static')



@app.route('/')
def start_page():
    return render_template('search.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/search', methods=['POST'])
def search_query():
    query={}
    for key, value in request.form.items():
        if value.strip() == '':
            continue
        if key in DB_MATERIALS_FIELDS:
            try:
                query[key]=db_lookup[key][1].convert(value)
            except Exception as e:
                return render_template('search.html', result_table=repr(e)+'<br >'+
                                    "Raised when tried to parse %s = %s"%(key, value))
    db=SLDDB(DB_FILE)
    res=db.search_material(**query)

    hidden_columns=[True for field in DB_MATERIALS_FIELDS]
    for row in res:
        for i, field in enumerate(DB_MATERIALS_FIELDS):
            if row[field] is not None and field not in DB_MATERIALS_HIDDEN_DATA:
                hidden_columns[i]=False
    flt_fields=[item for item in enumerate(DB_MATERIALS_FIELDS) if not hidden_columns[item[0]]]
    out='<table class="withborder">\n    <tr>\n        '
    out+='<th></th>'
    for i, field in flt_fields:
        out+='<th>%s</th>'%field.capitalize()
    out+='    </tr>\n'
    for row in res:
        out+='        <tr>'
        out+='<td><button type="submit" name="ID" id="ID" value="%i">select</button></td>'%row['ID']
        for i, field in flt_fields:
            out+='<td>%s</td>'%row[field]
        out+='</tr>\n'
    out+='</table>'
    return render_template('search.html', result_table=out)

@app.route('/material', methods=['POST'])
def select_material():
    if not 'ID' in request.form:
        return render_template('base.html')
    db=SLDDB(DB_FILE)
    res=db.search_material(ID=int(request.form['ID']))
    try:
        material=db.select_material(res[0])
    except Exception as e:
        return render_template('base.html', result_table=repr(e)+'<br >'+
                                                         "Raised when tried to parse material = %s"%res[0])

    out=result_table(material, res[0]['name'], res[0]['description'])
    E,delta=material.delta_vs_E()
    script=get_script(E, delta.real, delta.imag)
    return render_template('sldcalc.html', result_table=out, script=script)

@app.route('/material', methods=['GET'])
def calculate_sld():
    if 'formula' in request.args and 'density' in request.args:
        f=Formula(request.args['formula'], sort=False)
        db=SLDDB(DB_FILE)
        try:
            m=Material([(db.elements.get_element(element), amount) for element, amount in f],
                   dens=float(request.args['density']))
        except Exception as e:
            return render_template('sldcalc.html', result_table=repr(e)+'<br/>'+str(f))
        else:
            out=result_table(m, "User input")
            E, delta=m.delta_vs_E()
            script=get_script(E, delta.real, delta.imag)
            return render_template('sldcalc.html', result_table=out, script=script)
    return render_template('sldcalc.html')

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

@app.route('/api', methods=['GET'])
def api_query():
    if 'ID' in request.args:
        # handle as query
        return select_api()
    elif 'sldcalc' in request.args:
        return calc_api()
    elif 'get_fields' in request.args:
        return json.dumps([field for field in DB_MATERIALS_FIELDS if field not in DB_MATERIALS_HIDDEN_DATA])
    else:
        return search_api()

def calc_api():
    if 'formula' in request.args and 'density' in request.args:
        f=Formula(request.args['formula'], sort=False)
        db=SLDDB(DB_FILE)
        try:
            material=Material([(db.elements.get_element(element), amount) for element, amount in f],
                   dens=float(request.args['density']))
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

def select_api():
    db=SLDDB(DB_FILE)
    res=db.search_material(ID=int(request.args['ID']))
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

def search_api():
    query={}
    for key, value in request.args.items():
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

@app.route('/admin/')
def admin_page():
    return 'abc'