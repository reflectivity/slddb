import tempfile, os
from flask import request, render_template, flash, url_for, redirect
from werkzeug.utils import secure_filename

from .querydb import search_db
from .blender import collect_protein, collect_blend
from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup
from slddb.importers import CifImporter, PolymerSequence

input_fields=[field for field in DB_MATERIALS_FIELDS[1:]
              if field not in DB_MATERIALS_HIDDEN_DATA]

def fill_input(field, args):
    conv=db_lookup[field][1]
    if field in args:
        if conv.html_list:
            value=args.getlist(field)
        else:
            value=args[field]
    else:
        value=""
    return conv.html_input(field, value)

def get_input(field):
    return fill_input(field, request.args)

def get_unit(field):
    if db_lookup[field][3] is not None:
        unit=db_lookup[field][3]
        return f'({unit})'
    else:
        return ''

def input_form():
    return render_template('input.html', fields=input_fields, get_input=get_input, get_unit=get_unit)

def input_fill_cif(file_obj):
    filename=secure_filename(file_obj.filename)
    full_path=os.path.join(tempfile.gettempdir(), filename)
    file_obj.save(full_path)
    if filename.endswith('.gz'):
        import gzip
        txt=gzip.open(full_path, 'rb').read()
        os.remove(full_path)
        full_path=os.path.join(tempfile.gettempdir(), filename[:-3])
        open(full_path, 'wb').write(txt)
    data=CifImporter(full_path, validate=False)
    os.remove(full_path)

    if type(data.formula) is PolymerSequence:
        m=collect_protein('', data.formula)
        data['FU_volume']=m.fu_volume
        data.formula=m.formula

    def get_data_input(field):
        conv=db_lookup[field][1]
        if field == 'name':
            value=data.name
        elif field == 'formula':
            value=data.formula
        elif field in data:
            value=data[field]
        else:
            return get_input(field)
        return conv.html_input(field, value)
    return render_template('input.html', fields=input_fields, get_input=get_data_input, get_unit=get_unit)

def input_fill_blend(mtype, name, idstr):
    material=collect_blend(mtype, idstr)
    return redirect(url_for('input_page', name=name, formula=str(material.formula), FU_volume=material.fu_volume))

def input_material(args):
    db=SLDDB(DB_FILE)

    def get_input_args(field):
        return fill_input(field, args)

    if args['name']=='' or args['formula' ]=='':
        flash("You have to supply a name and Formula!")
        return render_template('input.html', fields=input_fields, get_input=get_input_args, get_unit=get_unit)


    useargs=dict(args.items())
    name=args['name']
    formula=args['formula']
    del(useargs['material'])
    del(useargs['name'])
    del(useargs['formula'])

    for key, value in list(useargs.items()):
        if db_lookup[key][1].html_list:
            useargs[key]=request.form.getlist(key)
        if value == '':
            del(useargs[key])
    try:
        db.add_material(name, formula, **useargs)
    except Exception as e:
        flash("Error when trying to insert data:\n"+repr(e))
        return render_template('input.html', fields=input_fields,
                               get_input=get_input_args, get_unit=get_unit)
    return search_db(useargs)

def edit_selection(ID, user):
    db=SLDDB(DB_FILE)
    res=db.search_material(ID=ID, filter_invalid=False)[0]

    def get_input_args(field):
        conv = db_lookup[field][1]
        if field in res:
            value = res[field]
            if value is None:
                value = ""
        else:
            value = ""
        return conv.html_input(field, value)

    return render_template('input.html', fields=input_fields, get_input=get_input_args, get_unit=get_unit,
                           editing_entry=ID)

def update_material(args):
    db=SLDDB(DB_FILE)

    def get_input_args(field):
        return fill_input(field, args)

    if args['name']=='' or args['formula' ]=='':
        flash("You have to supply a name and Formula!")
        return render_template('input.html', fields=input_fields, get_input=get_input_args, get_unit=get_unit,
                               editing_entry=args['ID'])


    useargs=dict(args.items())
    del(useargs['material'])
    del(useargs['ID'])

    for key, value in list(useargs.items()):
        if db_lookup[key][1].html_list:
            useargs[key]=request.form.getlist(key)
        if value=='':
            useargs[key]=None

    try:
        db.update_material(args['ID'], **useargs)
    except Exception as e:
        flash("Error when trying to insert data:\n"+repr(e))
        return render_template('input.html', fields=input_fields, get_input=get_input_args, get_unit=get_unit,
                               editing_entry=args['ID'])
    for key, value in list(useargs.items()):
        if value is None:
            del(useargs[key])
    return search_db(useargs)
