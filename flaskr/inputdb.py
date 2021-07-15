import tempfile, os
from flask import request, render_template
from werkzeug.utils import secure_filename

from .querydb import search_db
from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup
from slddb.importers import CifImporter

input_fields=[field for field in DB_MATERIALS_FIELDS[1:]
              if field not in DB_MATERIALS_HIDDEN_DATA]

def fill_input(field, args):
    conv=db_lookup[field][1]
    if field in args:
        if conv.__class__.__name__ == 'CMultiSelect':
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
    data=CifImporter(full_path)
    os.remove(full_path)

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

def input_material(args):
    db=SLDDB(DB_FILE)

    def get_input_args(field):
        return fill_input(field, args)

    if args['name']=='' or args['formula' ]=='':
        return render_template('input.html', fields=input_fields, get_input=get_input_args, get_unit=get_unit,
                               comment="You have to supply a name and Formula!")


    useargs=dict(args.items())
    name=args['name']
    formula=args['formula']
    del(useargs['material'])
    del(useargs['name'])
    del(useargs['formula'])

    for key, value in list(useargs.items()):
        if db_lookup[key][1].__class__.__name__ == 'CMultiSelect':
            useargs[key]=request.form.getlist(key)
        if value == '':
            del(useargs[key])
    try:
        db.add_material(name, formula, **useargs)
    except Exception as e:
        return render_template('input.html', fields=input_fields,
                               get_input=get_input_args, get_unit=get_unit,
                               comment="Error when trying to insert data:\n"+repr(e))
    return search_db(useargs)