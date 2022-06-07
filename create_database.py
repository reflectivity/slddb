from orsopy import slddb
from orsopy.slddb import __version__, dbconfig
# for flask use database file in startup folder
DB_FILE='slddb.db';dbconfig.DB_FILE=DB_FILE;slddb.DB_FILE=DB_FILE
from orsopy.slddb import SLDDB
from orsopy.slddb.dbconfig import DB_FILE
import sqlite3

if __name__=='__main__':
    db=SLDDB(DB_FILE)
    try:
        db.create_database()
        db.add_elements()
    except sqlite3.OperationalError:
        db.update_fields()
