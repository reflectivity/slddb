from flask import render_template

from slddb import SLDDB, DB_FILE
from slddb.dbconfig import DB_MATERIALS_FIELDS, DB_MATERIALS_HIDDEN_DATA, db_lookup

def search_db(query):
    db=SLDDB(DB_FILE)
    res=db.search_material(**query)
    hidden_columns=[True for field in DB_MATERIALS_FIELDS]
    for row in res:
        for i, field in enumerate(DB_MATERIALS_FIELDS):
            if row[field] is not None and field not in DB_MATERIALS_HIDDEN_DATA:
                hidden_columns[i]=False
    flt_fields=[item for item in enumerate(DB_MATERIALS_FIELDS) if not hidden_columns[item[0]]]
    out='<table class="withborder">\n    <tr>\n        '
    out+='<th></th>'
    for i, field in flt_fields:
        out+='<th>%s</th>'%field.capitalize()
    out+='    </tr>\n'
    for row in res:
        out+='        <tr>'
        out+='<td><button type="submit" name="ID" id="ID" value="%i">select</button></td>'%row['ID']
        for i, field in flt_fields:
            out+='<td>%s</td>'%row[field]
        out+='</tr>\n'
    out+='</table>'
    return render_template('search.html', result_table=out)

