from flask import request, render_template
from flask_login import current_user

from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup

main_fields=['name', 'formula', 'tags']
advanced_fields=['ID', 'physical_state', 'description','reference', 'CAS_No', 'temperature', 'comments', 'data_origin']

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
    return fill_input(field, request.form)

def show_search(**kwargs):
    if current_user.is_authenticated:
        user="%s <%s>"%(current_user.name, current_user.email)
    else:
        user=None
    return render_template('search.html', main_fields=main_fields, orso_user=user,
                           advanced_fields=advanced_fields, get_input=get_input, **kwargs)

def search_db(query, invalids=False, offset=0):
    db=SLDDB(DB_FILE)
    if current_user.is_authenticated:
        user="%s <%s>"%(current_user.name, current_user.email)
    else:
        user=None
    res=db.search_material(filter_invalid=not invalids, offset=offset, **query)
    if len(res)==0:
        return show_search(unsuccessful_query=query)
    hidden_columns=[True for field in DB_MATERIALS_FIELDS]
    advanced_search=any([key in advanced_fields for key in query.keys()])
    for row in res:
        row['color_class']='entry_used'
        if row['selected']==0:
            row['color_class']='entry_unused'
        if row['validated'] is not None:
            row['color_class']='orso_validated'
        if row['invalid'] is not None:
            row['color_class']='orso_invalid'
        for i, field in enumerate(DB_MATERIALS_FIELDS):
            if row[field] is not None and field not in DB_MATERIALS_HIDDEN_DATA:
                hidden_columns[i]=False
    if offset>0 or len(res)==100:
        count=db.count_material(filter_invalid=not invalids, **query)
        multipage='result range:<br />'
        if offset<99:
            multipage+=f' | {offset+1}-{offset+100} of {count} | <input type="submit" name="next" value="next">'
        elif offset>(count-100):
            multipage+=f'<input type="submit" name="prev" value="prev"> | {offset+1}-{count} of {count} |'
        else:
            multipage+=f'<input type="submit" name="prev" value="prev"> | {offset+1}-{offset+100} of {count} | ' \
                       f'<input type="submit" name="next" value="next">'
    else:
        multipage=None
    flt_fields=[item[1] for item in enumerate(DB_MATERIALS_FIELDS) if not hidden_columns[item[0]]]
    flt_fields_names=[item[1].capitalize() for item in enumerate(DB_MATERIALS_FIELDS) if not hidden_columns[item[0]]]
    hidden_fields_names=[item.capitalize() for item in DB_MATERIALS_HIDDEN_DATA]
    return render_template('search.html', flt_fields=flt_fields, flt_fields_names=flt_fields_names,
                           hidden_fields=DB_MATERIALS_HIDDEN_DATA, hidden_fields_names=hidden_fields_names,
                           query_result=res, orso_user=user, main_fields=main_fields,
                           advanced_fields=advanced_fields, get_input=get_input,
                           advanced_search=advanced_search, multipage=multipage, offset=offset)

