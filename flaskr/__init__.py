import json
import zipfile
import os
import time
from io import BytesIO
from flask import Flask
from flask import request, render_template, send_file, flash, redirect, url_for, make_response, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash, gen_salt
try:
    from werkzeug import FileWrapper
except ImportError:
    from wsgiref.util import FileWrapper

from orsopy import slddb
from orsopy.slddb import __version__, dbconfig
# for flask use database file in startup folder
DB_FILE='slddb.db';dbconfig.DB_FILE=DB_FILE;slddb.DB_FILE=DB_FILE
from orsopy.slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup
from orsopy.slddb.material import Formula
from orsopy.slddb import constants

from .api import calc_api, select_api, search_api
from .querydb import search_db, show_search, custom_query
from .calcsld import calculate_selection, calculate_user, validate_selection, invalidate_selection, \
    get_graph_xray, get_absorption_graph, get_deuteration_graph
from .inputdb import input_form, input_fill_cif, input_material, edit_selection, update_material, input_fill_blend
from .blender import calculate_blend, formula_from_pdb
from .periodic_table import get_periodic_table

app=Flask("ORSO SLD Data Base", template_folder='flaskr/templates',
          static_folder='flaskr/static')
# Try speeding up page load by using timed caching (reduce time lost due to TTFB)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600

try:
    app.config['SECRET_KEY']=open('flaskr/secret.key', 'rb').read()
except IOError:
    pass
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///flaskr/db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
db=SQLAlchemy()
db.init_app(app)

app.config['MAIL_SERVER']='10.0.0.103'
app.config['MAIL_PORT'] = 25
#app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '175ffa3adc24f2')
#app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '31fde10b3694db')
#app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USE_SSL'] = False
mail=Mail(app)
MAIL_SENDER='ORSO SLDdb Admin <slddb@esss.dk>'

login_manager=LoginManager()
login_manager.init_app(app)

@app.context_processor
def inject_version():
    return dict(slddb_version=__version__)

@app.context_processor
def inject_constants():
    return constants.__dict__

@app.context_processor
def inject_basics():
    return dict(len=len, str=str, float=float, int=int, list=list)

if app.debug:
    @app.after_request
    def add_security_headers(resp):
        resp.headers['Content-Security-Policy']="default-src 'self'"
        return resp

@app.route('/')
def start_page():
    return show_search()

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/input')
def input_page():
    return input_form()

@app.route('/input', methods=['POST'])
def eval_input():
    if not 'material' in request.form:
        try:
            return input_fill_cif(request.files['cif_file'])
        except Exception as e:
            flash(str(e))
            return  input_form()
    elif 'ID' in request.form:
        return update_material(request.form)
    else:
        return input_material(request.form)

@app.route('/search', methods=['GET'])
def search_query_post():
    return start_page()

@app.route('/search', methods=['POST'])
def search_query():
    query={}
    offset=0

    invalids=False
    for key, value in request.form.items():
        if 'offset' in request.form:
            offset=int(request.form['offset'])
        else:
            offset=0
        if value.strip() == '':
            continue
        if key in DB_MATERIALS_FIELDS:
            if db_lookup[key][1].html_list:
                value=request.form.getlist(key)
            try:
                cmp=db_lookup[key][1].comparator(value, key)
                cmp.query_args()
                cmp.query_string()
            except Exception as e:
                return show_search(error=repr(e)+'<br >'+"Raised when tried to parse %s = %s"%(key, value))
            else:
                query[key]=value
        if key=='show_invalid' and value:
            invalids=True
        if request.form.get('next') == 'next':
            offset+=100
        if request.form.get('prev') =='prev':
            offset-=100
        if request.form.get('Submit') == 'Submit':
            offset=0
    return search_db(query, invalids=invalids, offset=offset)

@app.route('/material', methods=['POST'])
def select_material():
    if 'Validate' in request.form:
        return validate_selection(int(request.form['Validate'].split('-')[1]), request.form['Validate'].split('-')[0])
    if 'Invalidate' in request.form:
        return invalidate_selection(int(request.form['Invalidate'].split('-')[1]), request.form['Invalidate'].split('-')[0])
    if 'Edit' in request.form:
        return edit_selection(int(request.form['Edit'].split('-')[1]), request.form['Edit'].split('-')[0])
    if not 'ID' in request.form:
        return render_template('base.html')
    return calculate_selection(int(request.form['ID']))


@app.route('/material', methods=['GET'])
def calculate_sld():
    if 'ID' in request.args:
        return calculate_selection(int(request.args['ID']))
    elif 'formula' in request.args and 'density' in request.args:
        try:
            f=Formula(request.args['formula'], sort=False)
        except Exception as e:
            return render_template('sldcalc.html',
                                   error=repr(e)+'<br >'+"Raised when tried to parse formula = '%s'"%request.args['formula'])
        else:
            return calculate_user(f, float(request.args['density'] or 1.0), float(request.args['mu'] or 0),
                                  request.args['densinput'], request.args['magninput'],
                                  name=request.args.get('name', default=None),
                                  material_description=request.args.get('description', default=""))
    else:
        return render_template('sldcalc.html')

@app.route('/bio_blender')
def bio_blender():
    return render_template('bio_blender.html')

@app.route('/bio_blender', methods=['POST'])
def combine_blender():
    mtype=request.form.get('molecule_type', default='protein')
    submit_type=request.form.get('submit', default='upload')
    if submit_type == 'Calculate SLD':
        try:
            return calculate_blend(mtype, request.form['name'], request.form['structure'])
        except Exception as e:
            return render_template('bio_blender.html',
                       error=repr(e)+'<br >'+"Raised when tried to parse composition = '%s'"%request.form['structure'])
    elif submit_type == 'Enter in Database':
        try:
            return input_fill_blend(mtype, request.form['name'], request.form['structure'])
        except Exception as e:
            return render_template('bio_blender.html',
                       error=repr(e)+'<br >'+"Raised when tried to parse composition = '%s'"%request.form['structure'])
    else:
        name, formula=formula_from_pdb(request.files['pdb_file'], sequence=int(request.form.get('sequence', 1)))
        return render_template('bio_blender.html', fill_formula=formula, fill_name=name)

@app.route('/api', methods=['GET'])
def api_query():
    if 'ID' in request.args:
        # handle as query
        return select_api(request.args)
    elif 'sldcalc' in request.args:
        return calc_api(request.args)
    elif 'get_fields' in request.args:
        return json.dumps([field for field in DB_MATERIALS_FIELDS if field not in DB_MATERIALS_HIDDEN_DATA],
                          indent='    ')
    else:
        return search_api(request.args)

@app.route('/api_download', methods=['GET'])
def api_download():
    record=api_query()
    mem_json=BytesIO()
    mem_json.write(record.encode('utf-8'))
    mem_json.seek(0)
    if 'ID' in request.args:
        result = send_file(mem_json, mimetype='application/json', as_attachment=True,
                           attachment_filename=f'orso_slddb_{request.args["ID"]}.json', conditional=True)
    else:
        result = send_file(mem_json, mimetype='application/json', as_attachment=True,
                           attachment_filename=f'orso_slddb_query_{time.strftime("%Y%H%M%S")}.json',
                           conditional=True, cache_timeout=0)
    return result

@app.route('/download_db')
def download_database():
    result=send_file(DB_FILE, mimetype='application/x-sqlite3', as_attachment=True,
                     attachment_filename=os.path.basename(DB_FILE), conditional=True)
    return result

@app.route('/download_api')
def download_api():
    # craete a zip file with the python package used on this server
    mem_zip=BytesIO()
    package_path=os.path.dirname(slddb.__file__)
    files=[n for n in os.listdir(package_path) if n.endswith('.py')]
    files+=[os.path.join('element_table', n)
            for n in os.listdir(os.path.join(package_path, 'element_table')) if n.endswith('.py')]
    files+=[os.path.join('element_table', 'nabs_geant4', n)
             for n in os.listdir(os.path.join(package_path, 'element_table', 'nabs_geant4')) if n.endswith('.npz')]

    with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for fi in files:
            zf.writestr(os.path.join('slddb', fi),
                        open(os.path.join(package_path, fi), 'rb').read())
    mem_zip.seek(0)
    result=send_file(mem_zip, mimetype='application/zip', as_attachment=True,
                     attachment_filename='slddb.zip', conditional=True)
    return result

@app.route('/periodic_table')
def periodic_table():
    return get_periodic_table(requested_element=request.args.get('sld_element', default=None),
                              plot_scale=request.args.get('plot_scale', default=None))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    admin = db.Column(db.Boolean(False))
    token_send = db.Column(db.String(100)) # is used for email tokens send to user for password reset

@login_manager.user_loader
def load_user(ID):
    return User.query.get(ID)


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login')) # if user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('start_page'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('start_page'))

@app.route('/admin')
@login_required
def admin():
    users=User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin', methods=['POST'])
@login_required
def add_user():
    if request.form.get('new_user', '')=='Submit' and request.form['user_email']!='' and request.form['user_name']!='':
        new_user=User(name=request.form['user_name'], email=request.form['user_email'], admin=False)
        db.session.add(new_user)
        db.session.commit()
        reset_password(new_user)
    users=User.query.all()
    for ui in users:
        if request.form.get('toggle_admin_%i'%ui.id, '')=='toggle':
            if ui.id==current_user.id:
                flash("You can't make yourself non-admin!")
            else:
                User.query.filter_by(id=ui.id).update(dict(admin=not ui.admin))
                db.session.commit()
            break
        if request.form.get('delete_user_%i'%ui.id, '')=='DELETE':
            if ui.id==current_user.id:
                flash("You can't delete yourself!")
            else:
                User.query.filter_by(id=ui.id).delete()
                db.session.commit()
                users=User.query.all()
            break
        if request.form.get('reset_password_%i'%ui.id, '')=='reset':
            if ui.id==current_user.id:
                flash("You can't reset your own password, you are already logged in!")
            else:
                reset_password(ui)
                users=User.query.all()
            break
    return render_template('admin.html', users=users)

@app.route('/admin_query')
@login_required
def admin_query():
    users=User.query.all()
    return render_template('admin_query.html', users=users)

@app.route('/admin_query', methods=['POST'])
@login_required
def run_admin_query():
    users=User.query.all()
    query=request.form.get('query_input', '')
    try:
        columns, results=custom_query(query)
        error=None
    except Exception as e:
        columns=None
        results=None
        error=repr(e)+'<br>'+"Raised when tried to execute query = '%s'"%query
    return render_template('admin_query.html', users=users, error=error,
                           query_input=query, columns=columns, results=results)

def reset_password(user):
    # create a reset password token and send an email to the user
    token=gen_salt(20)
    sha_token=generate_password_hash(token, method='sha256')
    User.query.filter_by(id=user.id).update(dict(token_send=sha_token, password=None))
    db.session.commit()
    url=url_for('user_query_password', _external=True, token=token, user_id=user.id)

    message=Message(subject='Password reset for ORSO SLDDB',
                    sender=current_user.email,
                    recipients=[user.email],
                    body=f"Dear {user.name},\n\nyour account password for the ORSO slddb has been reset. "
                         f"You can now set a new password with the following link:\n"
                         f"{url}\n\nKind regards,\nThe ORSO Team",
                    html=f"Dear {user.name},<br /><br />your account password for the ORSO slddb has been reset. "
                         f"You can now set a new password with the following link:<br />"
                         f"<a href='{url}'>{url}</a><br /><br />Kind regards,<br />The ORSO Team")
    mail.send(message)

@app.route('/reset_password', methods=["GET"])
def user_query_password():
    token=request.args.get('token', '')
    ID=int(request.args.get('user_id', '1'))
    user=User.query.get(ID)
    if user.token_send is not None and check_password_hash(user.token_send, token):
        return render_template('set_password.html', user_id=ID, token=token, user_email=user.email)
    else:
        flash('token is not active for user with id %i'%ID)
        return show_search()

@app.route('/reset_password', methods=["POST"])
def user_set_password():
    token=request.form.get('token', '')
    ID=int(request.form.get('user_id', '1'))
    user=User.query.get(ID)
    if user.token_send is not None and check_password_hash(user.token_send, token):
        pw=request.form.get('password', '')
        pw2=request.form.get('confirm_password', '')
        if pw!='' and pw==pw2:
            hash=generate_password_hash(pw, method='sha256')
            User.query.filter_by(id=user.id).update(dict(token_send=None, password=hash))
            db.session.commit()
            return redirect(url_for('login'))
        else:
            flash('Passwords have to be set and equal!')
            return render_template('set_password.html', user_id=ID, token=token)
    else:
        flash('token is not active for user with id %i'%ID)
        return show_search()

@app.route('/set_preference', methods=['POST'])
def set_preference():
    resp=make_response(redirect(request.form['return_link']))
    for key, value in request.form.items():
        if key in ['return_link']:
            continue
        resp.set_cookie(key, value, samesite='Strict')
    return resp

@app.route('/favicon.ico')
def favicon():
    response=app.send_static_file('favicon.ico')
    response.cache_control.max_age = 300
    return response

@app.route('/plot_xray.png', methods=['GET'])
def plot_xray():
    image_binary=get_graph_xray(request.args.get('formula', 'H2O'),
                                float(request.args.get('dens', 1.0)),
                                request.args.get('name', None),
                                bool(request.args.get('delta', False)))
    response = make_response(image_binary)
    response.cache_control.max_age = 300
    response.headers.set('Content-Type', 'image/png')
    return response

@app.route('/plot_nabs.png', methods=['GET'])
def plot_nabs():
    image_binary=get_absorption_graph(request.args.get('formula', 'H2O'),
                                float(request.args.get('dens', 1.0)),
                                request.args.get('name', None))
    response = make_response(image_binary)
    response.cache_control.max_age = 300
    response.headers.set('Content-Type', 'image/png')
    return response

@app.route('/plot_deuteration.png', methods=['GET'])
def plot_deuteration():
    image_binary=get_deuteration_graph(request.args.get('formula', 'H2O'),
                                float(request.args.get('dens', 1.0)),
                                request.args.get('name', None))
    response = make_response(image_binary)
    response.cache_control.max_age = 300
    response.headers.set('Content-Type', 'image/png')
    return response

