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

    def fill_input(field):
        conv=db_lookup[field][1]
        if field in args:
            value=args[field]
        else:
            value=""
        return conv.html_input()%{'field': field, 'value': value}

    if args['name']=='' or args['formula' ]=='':
        return render_template('input.html', fields=input_fields, get_input=fill_input,
                               comment="You have to supply a name and Formula!")


    useargs=dict(args.items())
    name=args['name']
    formula=args['formula']
    del(useargs['name'])
    del(useargs['formula'])

    for key, value in list(useargs.items()):
        if db_lookup[key][1].__class__.__name__ is 'CMultiSelect':
            useargs[key]=request.form.getlist(key)
            print(repr(useargs[key]))
        if value == '':
            del(useargs[key])
    try:
        db.add_material(name, formula, **useargs)
    except Exception as e:
        return render_template('input.html', fields=input_fields,
                               get_input=fill_input,
                               comment="Error when trying to insert data:\n"+repr(e))
    return search_db(useargs)