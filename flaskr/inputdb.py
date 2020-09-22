from flask import render_template

from .querydb import search_db
from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup

input_fields=[field for field in DB_MATERIALS_FIELDS[1:]
              if field not in DB_MATERIALS_HIDDEN_DATA]

def input_form():
    return render_template('input.html', fields=input_fields)

def input_material(args):
    db=SLDDB(DB_FILE)

    if args['name']=='' or args['formula' ]=='':
        return render_template('input.html', fields=input_fields,
                               comment="You have to supply a name and Formula!")

    name=args['name']
    formula=args['formula']

    args=dict(args.items())
    del(args['name'])
    del(args['formula'])

    for key, value in list(args.items()):
        if value == '':
            del(args[key])
    try:
        db.add_material(name, formula, **args)
    except Exception as e:
        return render_template('input.html', fields=input_fields,
                               comment="Error when trying to insert data:\n"+
                               repr(e))
    return search_db(args)