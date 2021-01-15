from flask import render_template

from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup

def search_db(query):
    db=SLDDB(DB_FILE)
    res=db.search_material(**query)
    hidden_columns=[True for field in DB_MATERIALS_FIELDS]
    for row in res:
        row['color']='#fff'
        if row['selected']==0:
            row['color']='#ddd'
        if row['validated'] is not None:
            row['color']='#dfd'
        for i, field in enumerate(DB_MATERIALS_FIELDS):
            if row[field] is not None and field not in DB_MATERIALS_HIDDEN_DATA:
                hidden_columns[i]=False
    flt_fields=[item[1] for item in enumerate(DB_MATERIALS_FIELDS) if not hidden_columns[item[0]]]
    flt_fields_names=[item[1].capitalize() for item in enumerate(DB_MATERIALS_FIELDS) if not hidden_columns[item[0]]]
    return render_template('search.html', flt_fields=flt_fields, flt_fields_names=flt_fields_names,
                           query_result=res)

