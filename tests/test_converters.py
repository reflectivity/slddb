import unittest
from datetime import datetime
from slddb.converters import CType, CLimited, CArray, CFormula, CComplex, Converter, CDate
from slddb.material import Formula
from numpy import array, ndarray, testing

class TestConverter(unittest.TestCase):
    def test_int(self):
        conv=CType(int, int)
        self.assertEqual(14, conv.revert(conv.convert(14)))
        self.assertEqual(conv.sql_type, "INT")

        self.assertTrue(type(conv.convert("13")) is int)
        self.assertTrue(type(conv.revert(13)) is int)

        with self.assertRaises(ValueError):
            conv.convert("13.4")
        with self.assertRaises(ValueError):
            conv.revert("13")

    def test_float(self):
        conv=CType(float, float)
        self.assertEqual(14.5, conv.revert(conv.convert(14.5)))
        self.assertEqual(conv.sql_type, "REAL")

        self.assertTrue(type(conv.convert("13.5")) is float)
        self.assertTrue(type(conv.revert(13.5)) is float)

        with self.assertRaises(ValueError):
            conv.convert("13a")
        with self.assertRaises(ValueError):
            conv.revert("13.5")

    def test_complex(self):
        conv=CComplex()
        self.assertEqual(14.5+3j, conv.revert(conv.convert(14.5+3j)))

        with self.assertRaises(ValueError):
            conv.convert("13a")
        with self.assertRaises(TypeError):
            conv.convert(b'abc')
        with self.assertRaises(ValueError):
            conv.revert(b"13.5")
        with self.assertRaises(TypeError):
            conv.revert("13.5")

    def test_str(self):
        conv=CType(str, str)
        self.assertEqual("abc", conv.revert(conv.convert("abc")))
        self.assertEqual(conv.sql_type, "TEXT")

        self.assertTrue(type(conv.convert("13")) is str)
        self.assertTrue(type(conv.revert("13")) is str)

        with self.assertRaises(ValueError):
            conv.revert(b"abc")
        with self.assertRaises(ValueError):
            conv.revert(14)

    def test_bytes(self):
        conv=CType(bytes, bytes)
        self.assertEqual(b"abc", conv.revert(conv.convert(b"abc")))
        self.assertEqual(conv.sql_type, "BLOB")

        self.assertTrue(type(conv.convert(b"13")) is bytes)
        self.assertTrue(type(conv.revert(b"13")) is bytes)

        with self.assertRaises(ValueError):
            conv.revert("abc")
        with self.assertRaises(ValueError):
            conv.revert(14)

    def test_formula(self):
        conv=CFormula()
        start_formula=str(Formula('Fe2O3'))
        self.assertEqual(start_formula, conv.revert(conv.convert(start_formula)))
        with self.assertRaises(ValueError):
            conv.convert("Beer")

    def test_date(self):
        conv=CDate()
        now=datetime.now()
        # round off the sub-seconds
        now=datetime.strptime(now.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        self.assertEqual(now, conv.revert(conv.convert(now)))
        self.assertEqual(now, conv.revert(conv.convert(now.strftime('%Y-%m-%d %H:%M:%S'))))

    def test_non_sqtype(self):
        with self.assertRaises(TypeError):
            conv=CType(str, array)

    def test_limited_float(self):
        conv=CLimited(float, float, -3.0, 5.4)
        self.assertEqual(3.5, conv.revert(conv.convert(3.5)))
        self.assertEqual(conv.sql_type, "REAL")

        self.assertTrue(type(conv.convert("3.5")) is float)
        self.assertTrue(type(conv.revert(3.5)) is float)

        with self.assertRaises(ValueError):
            conv.convert("13a")
        with self.assertRaises(ValueError):
            conv.revert("13.5")
        self.assertTrue(conv.validate(-3.0))
        self.assertTrue(conv.validate(5.4))
        self.assertFalse(conv.validate(-3.1))
        self.assertFalse(conv.validate(5.5))


    def test_array_general(self):
        conv=CArray()
        a=array([1,2,4,5,6])
        b=array([[1,2,],[3,4,]])

        self.assertTrue(type(conv.revert(conv.convert(a))) is ndarray)

        testing.assert_array_equal(a, conv.revert(conv.convert(a)))
        testing.assert_array_equal(b, conv.revert(conv.convert(b)))

        self.assertIsNone(conv.revert(None))
        with self.assertRaises(TypeError):
            conv.revert(conv.convert(a).decode('ascii'))

    def test_array_dimension(self):
        conv=CArray(ndim=1)
        a=array([1,2,4,5,6])
        testing.assert_array_equal(a, conv.revert(conv.convert(a)))

        with self.assertRaises(ValueError):
            b=array([[1,2,],[3,4,]])
            conv.revert(conv.convert(b))

    def test_array_shape(self):
        conv=CArray(shape=(2,2))

        with self.assertRaises(ValueError):
            a=array([1,2,4,5,6])
            conv.convert(a)
        with self.assertRaises(ValueError):
            a=array([[1,2,4],[5,6,7]])
            conv.convert(a)

        b=array([[1,2,],[3,4,]])
        testing.assert_array_equal(b, conv.revert(conv.convert(b)))

    def test_class(self):
        with self.assertRaises(NotImplementedError):
            Converter()

        class Test(Converter):
            def __init__(self):
                pass

        t=Test()
        with self.assertRaises(NotImplementedError):
            t.convert(12)
        self.assertEqual(t.revert(13), 13)

    def test_validate(self):
        conv=CType(float, float)
        self.assertTrue(conv.validate(13.4))
        self.assertFalse(conv.validate('abc'))

        conv=CLimited(float, float, -3.0, 5.4)
        self.assertFalse(conv.validate(-4.0))
        self.assertFalse(conv.validate('abc'))

