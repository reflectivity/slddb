from slddb import SLDDB
from slddb.dbconfig import DB_FILE

if __name__=='__main__':
    db=SLDDB(DB_FILE)
    db.create_database()
    db.add_elements()
