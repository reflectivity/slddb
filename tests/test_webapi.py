import unittest
import os, sys
import tempfile
import zipfile
import shutil
from urllib import request


class TestWebAPI(unittest.TestCase):
    server_available=True

    @classmethod
    def setUpClass(cls):
        # create a temporary fold to download python api and store database file
        cls.path=os.path.join(tempfile.gettempdir(), 'slddb_test')
        if os.path.exists(cls.path):
            shutil.rmtree(cls.path) # cleanup possible earlier runs
        os.makedirs(cls.path)

        # try to download the module from website
        try:
            res=request.urlopen('http://127.0.0.1:5000/download_api', timeout=500)
        except:
            cls.server_available=False
            print("Server unreachable to download python api")
            return
        with open(os.path.join(cls.path, 'slddb.zip'), 'wb') as f:
            try:
                f.write(res.read())
            except:
                cls.server_available=False
                print("Server unreachable to download python api")
                return
        # clear all modules of slddb
        for key in list(sys.modules.keys()):
            if key.startswith('slddb'):
                del sys.modules[key]

        # make sure the temporary directory is the first search path for new modules
        sys.path.insert(0, cls.path)
        with zipfile.ZipFile(os.path.join(cls.path, 'slddb.zip')) as zf:
            zf.extractall(cls.path)

        global api, slddb
        import slddb
        from slddb import api, webapi, dbconfig
        # overwrite local server URL
        cls._api_url=dbconfig.WEBAPI_URL
        dbconfig.WEBAPI_URL='http://127.0.0.1:5000/'
        webapi.WEBAPI_URL=dbconfig.WEBAPI_URL
        # set a temporary database file
        dbconfig.DB_FILE=os.path.join(cls.path, 'slddb.db')
        slddb.DB_FILE=dbconfig.DB_FILE
        webapi.DB_FILE=slddb.DB_FILE

    @classmethod
    def tearDownClass(cls):
        try:
            global api
            try:
                api.db.db.close()
            except:
                pass
            del(api)
        except NameError:
            pass
        # delete temporary folder with all files
        shutil.rmtree(cls.path)

        # clear all modules of slddb
        for key in list(sys.modules.keys()):
            if key.startswith('slddb'):
                del sys.modules[key]

    def test_a_downloaddb(self):
        if not self.server_available:
            return
        # make sure the path of the module is correct and that the database has not been downloaded
        self.assertTrue(api.first_access)
        #self.assertEqual(slddb.__file__, os.path.join(self.path, 'slddb', '__init__.py'))
        self.assertFalse(os.path.exists(slddb.DB_FILE))
        # test of database download
        api.download_db()
        self.assertTrue(os.path.exists(slddb.DB_FILE))
        mtime=os.path.getmtime(slddb.DB_FILE)
        # test of second download to overwrite
        api.download_db()
        m2time=os.path.getmtime(slddb.DB_FILE)
        self.assertNotEqual(mtime, m2time)
        # test error when server does not exist
        from urllib.error import URLError
        from slddb import webapi, dbconfig
        webapi.WEBAPI_URL='http://doesnot.exist/'
        with self.assertRaises(URLError):
            api.download_db()
        webapi.WEBAPI_URL=dbconfig.WEBAPI_URL
        # test error when file is wrong
        api.db_suburl='download_api'
        with self.assertRaises(ValueError):
            api.download_db()
        api.db_suburl='download_db'

    def test_b_check(self):
        if not self.server_available:
            return
        api.first_access=True
        if os.path.isfile(slddb.DB_FILE):
            os.remove(slddb.DB_FILE)
        api.check()
        self.assertFalse(api.first_access)
        api.first_access=True
        api.check()
        self.assertFalse(api.first_access)
        api.check()
        # check the update case
        api.db.db.close()
        del(api.db)
        api.first_access=True
        api.max_age=-1
        api.check()
        api.max_age=1
        # check warning if download url doesn't work during update
        api.db.db.close()
        del(api.db)
        api.first_access=True
        api.max_age=-1

        from slddb import webapi, dbconfig
        webapi.WEBAPI_URL='http://doesnot.exist/'
        with self.assertWarns(UserWarning):
            api.check()
        api.max_age=1
        webapi.WEBAPI_URL=dbconfig.WEBAPI_URL
        api.check()


    def test_c_query(self):
        if not self.server_available:
            return
        res=api.search(fomula="Fe2O3")
        self.assertGreater(len(res), 0)
        self.assertIn('density', res[0])

    def test_c_material(self):
        if not self.server_available:
            return
        mat=api.material(1)
        self.assertEqual(mat.__class__.__name__, 'Material')

    def test_c_custom(self):
        if not self.server_available:
            return
        mat=api.custom(formula='Au', dens=19.3)
        self.assertEqual(mat.__class__.__name__, 'Material')

    def test_d_local(self):
        if not self.server_available:
            return
        # test database access if server is unavailable
        from slddb import webapi, dbconfig
        webapi.WEBAPI_URL='http://doesnot.exist/'

        with self.subTest(msg='local search', i=0):
            # first search drop connection
            api.use_webquery=True
            api.search(formula='Fe2O3')
            self.assertFalse(api.use_webquery)
            res=api.search(formula='Fe2O3')
            self.assertGreater(len(res), 0)
            self.assertIn('density', res[0])
        with self.subTest(msg='local material', i=0):
            api.use_webquery=True
            mat=api.material(1)
            self.assertFalse(api.use_webquery)
            mat=api.material(1)
            self.assertEqual(mat.__class__.__name__, 'Material')
        webapi.WEBAPI_URL=dbconfig.WEBAPI_URL

