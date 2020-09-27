from flask import request, render_template

from .querydb import search_db
from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup

input_fields=[field for field in DB_MATERIALS_FIELDS[1:]
              if field not in DB_MATERIALS_HIDDEN_DATA]

def get_input(field):
    conv=db_lookup[field][1]
    if field in request.args:
        value=request.args[field]
    else:
        value=""
    return conv.html_input()%{'field': field, 'value': value}

def input_form():
    return render_template('input.html', fields=input_fields, get_input=get_input)

def input_material(args):
    db=SLDDB(DB_FILE)

    if args['name']=='' or args['formula' ]=='':
        return render_template('input.html', fields=input_fields, get_input=get_input,
                               comment="You have to supply a name and Formula!")

    name=args['name']
    formula=args['formula']

    args=dict(args.items())
    del(args['name'])
    del(args['formula'])

    for key, value in list(args.items()):
        if db_lookup[key][1].__class__.__name__ is 'CMultiSelect':
            args[key]=request.form.getlist(key)
            print(repr(args[key]))
        if value == '':
            del(args[key])
    try:
        db.add_material(name, formula, **args)
    except Exception as e:
        return render_template('input.html', fields=input_fields, get_input=get_input,
                               comment="Error when trying to insert data:\n"+
                               repr(e))
    return search_db(args)