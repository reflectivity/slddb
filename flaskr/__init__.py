import json
import zipfile
import os
from io import BytesIO
from flask import Flask
from flask import request, render_template, send_file, make_response
try:
    from werkzeug import FileWrapper
except ImportError:
    from wsgiref.util import FileWrapper

import slddb
from slddb import __version__, dbconfig
# for flask use database file in startup folder
DB_FILE='slddb.db';dbconfig.DB_FILE=DB_FILE;slddb.DB_FILE=DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup
from slddb.material import Formula

from .api import calc_api, select_api, search_api
from .querydb import search_db
from .calcsld import calculate_selection, calculate_user, validate_selection
from .inputdb import input_form, input_material

app=Flask("ORSO SLD Data Base", template_folder='flaskr/templates',
          static_folder='flaskr/static')

@app.context_processor
def inject_version():
    return dict(slddb_version=__version__)

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

@app.route('/admin', methods=['GET'])
def admin_page():
    user=request.args['user']
    resp=make_response(render_template('about.html'))
    resp.set_cookie('userID', user)
    return resp


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
                return render_template('search.html', error=repr(e)+'<br >'+
                                    "Raised when tried to parse %s = %s"%(key, value))
    return search_db(query)

@app.route('/material', methods=['POST'])
def select_material():
    if 'Validate' in request.form:
        return validate_selection(int(request.form['Validate'].split('-')[1]), request.form['Validate'].split('-')[0])
    if not 'ID' in request.form:
        return render_template('base.html')
    return calculate_selection(int(request.form['ID']))


@app.route('/material', methods=['GET'])
def calculate_sld():
    if 'formula' in request.args and 'density' in request.args:
        try:
            f=Formula(request.args['formula'], sort=False)
        except Exception as e:
            return render_template('sldcalc.html',
                                   error=repr(e)+'<br >'+"Raised when tried to parse formula = %s"%request.args['formula'])
        else:
            return calculate_user(f, float(request.args['density'] or 0),
                                  request.args['densinput']=='density',
                                  float(request.args['mu'] or 0))
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

@app.route('/download_db')
def download_database():
    result=send_file(DB_FILE, mimetype='application/x-sqlite3', as_attachment=True,
                     attachment_filename=os.path.basename(DB_FILE), conditional=False)
    return result

@app.route('/download_api')
def download_api():
    # craete a zip file with the python package used on this server
    mem_zip=BytesIO()
    package_path=os.path.dirname(slddb.__file__)
    files=[n for n in os.listdir(package_path) if n.endswith('.py')]

    with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for fi in files:
            zf.writestr(os.path.join('slddb', fi),
                        open(os.path.join(package_path, fi), 'rb').read())
    mem_zip.seek(0)
    result=send_file(mem_zip, mimetype='application/zip', as_attachment=True,
                     attachment_filename='slddb.zip', conditional=False)
    return result

# @app.route('/admin/')
# def admin_page():
#     return 'abc'