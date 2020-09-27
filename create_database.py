from slddb import SLDDB
from slddb.dbconfig import DB_FILE
import sqlite3

if __name__=='__main__':
    db=SLDDB(DB_FILE)
    try:
        db.create_database()
        db.add_elements()
    except sqlite3.OperationalError:
        db.update_fields()
