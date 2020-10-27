import json
from flask import Flask
from flask import request, render_template

from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup
from slddb.material import Material, Formula

from .api import calc_api, select_api, search_api
from .querydb import search_db
from .calcsld import calculate_selection, calculate_user
from .inputdb import input_form, input_material

app=Flask("ORSO SLD Data Base", template_folder='slddb/flaskr/templates',
          static_folder='slddb/flaskr/static')

@app.route('/')
def start_page():
    return render_template('search.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/input')
def input_page():
    return input_form()

@app.route('/input', methods=['POST'])
def eval_input():
    return input_material(request.form)


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
    return search_db(query)

@app.route('/material', methods=['POST'])
def select_material():
    if not 'ID' in request.form:
        return render_template('base.html')
    return calculate_selection(int(request.form['ID']))


@app.route('/material', methods=['GET'])
def calculate_sld():
    if 'formula' in request.args and 'density' in request.args:
        f=Formula(request.args['formula'], sort=False)
        return calculate_user(f, float(request.args['density']),
                              request.args['densinput']=='density',
                              float(request.args['mu']))
    else:
        return render_template('sldcalc.html')

@app.route('/api', methods=['GET'])
def api_query():
    if 'ID' in request.args:
        # handle as query
        return select_api(request.args)
    elif 'sldcalc' in request.args:
        return calc_api(request.args)
    elif 'get_fields' in request.args:
        return json.dumps([field for field in DB_MATERIALS_FIELDS if field not in DB_MATERIALS_HIDDEN_DATA])
    else:
        return search_api(request.args)


@app.route('/admin/')
def admin_page():
    return 'abc'
