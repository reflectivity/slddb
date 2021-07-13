from flask import request, render_template
from flask_login import current_user

from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup

main_fields=['name', 'formula', 'tags']
advanced_fields=['physical_state', 'description','reference', 'CAS_No', 'temperature', 'comments', 'data_origin']

def get_input(field):
    conv=db_lookup[field][1]
    if field in request.form:
        value=request.form[field]
    else:
        value=""
    return conv.html_input()%{'field': field, 'value': value}

def show_search():
    return render_template('search.html', main_fields=main_fields,
                           advanced_fields=advanced_fields, get_input=get_input)

def search_db(query):
    db=SLDDB(DB_FILE)
    if current_user.is_authenticated:
        user="%s <%s>"%(current_user.name, current_user.email)
    else:
        user=None
    res=db.search_material(filter_invalid=user is None, **query)
    hidden_columns=[True for field in DB_MATERIALS_FIELDS]
    advanced_search=any([key in advanced_fields for key in query.keys()])
    for row in res:
        row['color']='#fff'
        if row['selected']==0:
            row['color']='#ddd'
        if row['validated'] is not None:
            row['color']='#dfd'
        if row['invalid'] is not None:
            row['color']='#fdd'
        for i, field in enumerate(DB_MATERIALS_FIELDS):
            if row[field] is not None and field not in DB_MATERIALS_HIDDEN_DATA:
                hidden_columns[i]=False
    flt_fields=[item[1] for item in enumerate(DB_MATERIALS_FIELDS) if not hidden_columns[item[0]]]
    flt_fields_names=[item[1].capitalize() for item in enumerate(DB_MATERIALS_FIELDS) if not hidden_columns[item[0]]]
    hidden_fields_names=[item.capitalize() for item in DB_MATERIALS_HIDDEN_DATA]
    return render_template('search.html', flt_fields=flt_fields, flt_fields_names=flt_fields_names,
                           hidden_fields=DB_MATERIALS_HIDDEN_DATA, hidden_fields_names=hidden_fields_names,
                           query_result=res, orso_user=user, main_fields=main_fields,
                           advanced_fields=advanced_fields, get_input=get_input, advanced_search=advanced_search)

