import unittest
import json
from slddb import SLDDB


class TestMaterialDB(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=SLDDB(':memory:')
        cls.db.create_database()

    def test_add_item(self):
        self.db.add_material('Iron Oxide', 'Fe2O3', density=5.24)
        self.db.add_material('Nickel', 'Ni', density="8.9")

        with self.assertRaises(KeyError):
            self.db.add_material('TestMaterial', 'Fe2O3', beer='beer', density=2.0)
        with self.assertRaises(ValueError):
            self.db.add_material('TestMaterial', 'Fe2O3')

    def test_search(self):
        self.db.add_material('Iron Oxide', 'Fe2O3', density=5.24)
        self.db.add_material('Nickel', 'Ni', density="8.9")

        res=self.db.search_material(name='iron')[0]
        self.assertEqual(res['density'], 5.24)
        self.assertEqual(res['name'], 'Iron Oxide')
        self.assertEqual(res['formula'], 'Fe2O3')
        self.assertIsNone(res['FU_volume'])

    def test_serializable_search(self):
        self.db.add_material('Iron Oxide', 'Fe2O3', density=5.24)
        res=self.db.search_material(name='iron', serializable=True)[0]
        json.dumps(res)

    def test_search_fail(self):
        with self.assertRaises(KeyError):
            self.db.search_material(beer='beer')

    def test_search_empty(self):
        res=self.db.search_material()
        res2=self.db.search_material()
        self.assertEqual(res[0]['accessed'], res2[0]['accessed'])

    def test_search_andor(self):
        self.db.add_material('Iron Oxide light', 'Fe2O3', density=5.0)
        self.db.add_material('Iron Oxide heavy', 'Fe2O3', density=6.0)
        res1=self.db.search_material(name='iron', density=5.0)
        res2=self.db.search_material(name='iron', density=5.0, join_and=False)
        self.assertNotEqual(res1, res2)


    def test_selection(self):
        self.db.add_material('To Select', 'Pb', density=11.4)
        res=self.db.search_material(density=11.4)
        mat=self.db.select_material(res[0])
        self.assertAlmostEqual(mat.dens, 11.4)


    def test_access_counter(self):
        self.db.add_material('Iron Oxide', 'Fe2O3', density=5.24)
        r1=self.db.search_material(name='iron')[0]['accessed']
        r2=self.db.search_material(name='iron')[0]['accessed']
        r3=self.db.search_material(name='iron')[0]['accessed']
        self.assertEqual(r1+1,r2)
        self.assertEqual(r2+1,r3)

    def test_add_elements(self):
        self.db.add_elements()
