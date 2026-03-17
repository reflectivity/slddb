from pathlib import Path
from slddb import dbconfig
import slddb

# for flask use database file in startup folder
DB_FILE = Path("instance", "slddb.db")
DB_FILE.parent.mkdir(exist_ok=True)
dbconfig.DB_FILE=DB_FILE
slddb.DB_FILE=DB_FILE

from slddb import SLDDB
from slddb.dbconfig import DB_FILE
import sqlite3

if __name__=='__main__':
    db=SLDDB(DB_FILE)
    try:
        db.create_database()
    except sqlite3.OperationalError:
        db.update_fields()
